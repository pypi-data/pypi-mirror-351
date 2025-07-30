from autopysta import CustomModelBuilder, params_cust, Point
import functools
from typing import Protocol, Callable
import ast, inspect, textwrap

class AccelCtx(Protocol):
    leader: Point
    follower: Point
    params: params_cust

    def has_leader(self) -> bool:
        pass
    def has_follower(self) -> bool:
        pass


class SpacingCtx(Protocol):
    v_leader: float
    v_follower: float
    params: params_cust

class WaveSpeedCtx(Protocol):
    leader: Point
    follower: Point
    params: params_cust

    def has_leader(self) -> bool:
        pass
    def has_follower(self) -> bool:
        pass

class FreeFlowCtx(Protocol):
    params: params_cust

# Type aliases for callbacks
AccelFn     = Callable[[AccelCtx],    float]
SpacingFn   = Callable[[SpacingCtx],  float]
WaveSpeedFn = Callable[[WaveSpeedCtx],float]
FreeFlowFn  = Callable[[FreeFlowCtx], float]


# Valid fields for each context type
_ALLOWED_FIELDS = {
    "accel": {
        "leader": True,
        "follower": True,
        "has_leader": True,
        "has_follower": True,
        "v_leader": False,
        "v_follower": False,
        "params": True
    },
    "spacing": {
        "leader": False,
        "follower": False,
        "has_leader": False,
        "has_follower": False,
        "v_leader": True,
        "v_follower": True,
        "params": True
    },
    "wave_speed": {
        "leader": True,
        "follower": True,
        "has_leader": True,
        "has_follower": True,
        "v_leader": False,
        "v_follower": False,
        "params": True
    },
    "free_flow": {
        "leader": False,
        "follower": False,
        "v_leader": False,
        "v_follower": False,
        "has_leader": False,
        "has_follower": False,
        "params": True
    }
}

def _assert_valid_build_time(fn, kind: str):
    # grab & dedent the callback’s source
    src = inspect.getsource(fn)
    src = textwrap.dedent(src)

    # parse into AST once
    tree = ast.parse(src)
    allowed = _ALLOWED_FIELDS[kind]

    class Checker(ast.NodeVisitor):
        def visit_Attribute(self, node: ast.Attribute):
            # only flag direct “ctx.X”
            if isinstance(node.value, ast.Name) and node.value.id == "ctx":
                name = node.attr
                if name not in allowed:
                    raise AttributeError(
                        f"Use of '{name}' not allowed in {kind}()"
                    )
                if not allowed[name]:
                    raise RuntimeError(
                        f"Access to '{name}' is always None in {kind}()"
                    )
            self.generic_visit(node)

    Checker().visit(tree)


class CustomModelBuilderProxy:
    def __init__(self):
        self._builder = CustomModelBuilder()
        self._defined = {k: False for k in _ALLOWED_FIELDS}

    def accel(self, fn=None):
        if fn is None:
            return lambda f: self.accel(f)
        # mark & validate *once* at decoration time
        self._defined["accel"] = True
        _assert_valid_build_time(fn, "accel")
        # register the raw fn with C++
        self._builder.set_accel(fn)
        return fn


    def spacing(self, fn=None):
        if fn is None:
            return lambda f: self.spacing(f)
        self._defined["spacing"] = True
        _assert_valid_build_time(fn, "spacing")
        self._builder.set_spacing(fn)
        return fn


    def wave_speed(self, fn=None):
        if fn is None:
            return lambda f: self.wave_speed(f)
        self._defined["wave_speed"] = True
        _assert_valid_build_time(fn, "wave_speed")
        self._builder.set_wave_speed(fn)
        return fn


    def free_flow(self, fn=None):
        if fn is None:
            return lambda f: self.free_flow(f)
        self._defined["free_flow"] = True
        _assert_valid_build_time(fn, "free_flow")
        self._builder.set_free_flow(fn)
        return fn

    def params(self, param_dict):
        p = params_cust()
        for k, v in param_dict.items():
            p.add(k, v)
        self._builder.set_params(p)

    def build(self):
        missing = [k for k, v in self._defined.items() if not v]
        if missing:
            raise RuntimeError(f"Missing callbacks: {', '.join(missing)}")
        return self._builder.build()


def custom_model(fn):
    """Decorator to wire up the proxy, run user code once, then build."""
    @functools.wraps(fn)
    def wrapper():
        proxy = CustomModelBuilderProxy()
        fn(proxy)
        return proxy.build()
    return wrapper
