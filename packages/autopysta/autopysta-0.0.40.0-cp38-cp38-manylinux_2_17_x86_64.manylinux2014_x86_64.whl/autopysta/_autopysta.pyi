"""
Autopysta Module
"""
from __future__ import annotations
import typing
__all__ = ['AutopystaException', 'Box', 'Clock', 'CppException', 'Creator', 'CreatorMartinezJin2020', 'CustomModelBuilder', 'DistributionType', 'FixedDemandCreator', 'FixedObject', 'FixedStateCreator', 'GeneralizedTrajectory', 'Geometry', 'LCM', 'ModelContext', 'MultiModelDemandCreator', 'MultiModelStateCreator', 'Point', 'RandomGenerator', 'Results', 'RoadObject', 'Simulation', 'SimulationBuilder', 'StaticTrajectory', 'StochasticDemandCreator', 'StochasticStateCreator', 'Test', 'Trajectory', 'Vehicle', 'accurate_custom_model', 'example_car', 'fast_custom_model', 'gipps', 'idm', 'laval', 'lcm_force', 'lcm_gipps', 'lcm_laval', 'linear', 'martinez_jin_2020', 'model', 'newell', 'newell_constrained_timestep', 'newell_random_acceleration', 'no_lch', 'p_gipps', 'p_idm', 'p_laval', 'p_lcm_force', 'p_lcm_gipps', 'p_lcm_laval', 'p_linear', 'p_martinez_jin_2020', 'p_newell', 'p_newell_random_acceleration', 'params', 'params_cust', 'version']
class AutopystaException(RuntimeError):
    pass
class Box:
    """
    The `Box` class defines a time-space region for measuring Edie's flow and
    density.
    
    A `Box` is a rectangular area in time and space used to calculate flow and
    density values based on the vehicle trajectories that pass through it.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, x_min: float, x_max: float, t_min: float, t_max: float) -> None:
        """
        Constructor that defines a time-space box for measuring flow and density.
        
        Parameter ``xa``:
            Lower bound of the distance range.
        
        Parameter ``xb``:
            Upper bound of the distance range.
        
        Parameter ``ta``:
            Lower bound of the time range.
        
        Parameter ``tb``:
            Upper bound of the time range.
        """
    def contains(self, point: Point) -> bool:
        """
        Checks whether a point lies within the box.
        
        Parameter ``p``:
            The point to check.
        
        Returns:
            `true` if the point is inside the box, `false` otherwise.
        """
    def get_edie(self) -> list[float]:
        """
        Computes Edie's flow and density values for the box.
        
        Returns:
            A vector containing flow (Q) and density (K) values for the box.
        """
    def get_intersection(self, p1: Point, p2: Point) -> Point:
        """
        Computes the intersection of two points with the edges of the box.
        
        This method calculates the intersection point of a line segment defined by two
        points (p1, p2) with the edges of the box.
        
        Parameter ``p1``:
            First point of the line segment.
        
        Parameter ``p2``:
            Second point of the line segment.
        
        Returns:
            The point of intersection with the box edges.
        """
    def inter_hor(self, p1: Point, p2: Point, x: float) -> Point:
        """
        Calculates the intersection with a horizontal line at a given x value.
        
        Parameter ``p1``:
            First point of the line segment.
        
        Parameter ``p2``:
            Second point of the line segment.
        
        Parameter ``x``:
            The x-coordinate of the horizontal line.
        
        Returns:
            The intersection point.
        """
    def inter_ver(self, p1: Point, p2: Point, t: float) -> Point:
        """
        Calculates the intersection with a vertical line at a given t value.
        
        Parameter ``p1``:
            First point of the line segment.
        
        Parameter ``p2``:
            Second point of the line segment.
        
        Parameter ``t``:
            The t-coordinate of the vertical line.
        
        Returns:
            The intersection point.
        """
    def print(self) -> None:
        """
        Prints the trails (vehicle paths) that pass through the box.
        
        This is used for debugging and visualization purposes.
        """
class Clock:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def get_dt() -> float:
        """
        Get the fixed time step.
        """
    @staticmethod
    def get_time() -> float:
        """
        Get the current simulation time.
        """
    @staticmethod
    def is_updated() -> bool:
        """
        Check if the clock is updated.
        """
    @staticmethod
    def set_dt(arg0: float) -> None:
        """
        Set the fixed time step.
        """
    @staticmethod
    def set_is_updated(arg0: bool) -> None:
        """
        Set the clock update state.
        """
    @staticmethod
    def set_time(arg0: float) -> None:
        """
        Set the current simulation time.
        """
class CppException:
    """
    A custom exception class for handling errors in the Autopysta application.
    
    This class provides detailed error handling with error codes and messages,
    facilitating better debugging and error tracking within the application. It
    integrates with Python and can be raised and caught as a Python exception.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, code: int, message: str) -> None:
        """
        Constructs an Exception with a specific error code and message.
        
        Parameter ``code``:
            Error code representing the type of error.
        
        Parameter ``message``:
            Detailed error message providing context for the exception.
        """
    def __str__(self) -> str:
        ...
    def code(self) -> int:
        """
        Retrieves the error code associated with the exception.
        
        Returns:
            An integer representing the error code.
        """
    def message(self) -> str:
        """
        Retrieves the detailed error message.
        
        Returns:
            A const reference to a string containing the error message.
        """
    def what(self) -> str:
        """
        Provides a description of the exception, including the error code and message.
        
        Returns:
            A C-style string with a combined error code and message, safe for logging.
        """
class Creator:
    """
    Base class for generating vehicles in a traffic simulation.
    
    The `creator` class defines the logic for creating new vehicles either at the
    start of the simulation or during runtime. It handles the vehicle creation
    process based on specified models, parameters, and traffic conditions (such as
    gaps between vehicles). Derived classes should implement specific creation
    logic.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def create(self, leader: Point, immediate_follower: bool = False) -> Vehicle:
        """
        Creates a new vehicle based on the current leader's position.
        
        This method checks whether it is possible to create a new vehicle based on the
        leader's state. If so, it generates a new vehicle at an appropriate position
        relative to the leader. If `immediate_follower` is true, the new vehicle will be
        placed just behind the leader; otherwise, it will start at the beginning of the
        lane.
        
        Parameter ``leader``:
            The point representing the leader's current state (position, speed).
        
        Parameter ``immediate_follower``:
            Whether the new vehicle should follow immediately behind the leader.
        
        Returns:
            A pointer to the created vehicle, or `nullptr` if no vehicle was created.
        """
    def create_no_leader(self, lane: int) -> Vehicle:
        """
        Creates a new vehicle in an empty lane.
        
        This method creates a new vehicle in a lane that has no leading vehicle. It is
        meant to be used for initializing lanes with vehicles at the beginning of the
        simulation or adding vehicles dynamically when no leader is present.
        
        Parameter ``lane``:
            The lane number in which to create the vehicle.
        
        Returns:
            A pointer to the created vehicle, or `nullptr` if no vehicle was created.
        """
    def initialize_state(self, leader: Point) -> list[Vehicle]:
        """
        Initializes vehicles in the first simulation timestep.
        
        This method is used to create and position vehicles during the first timestep of
        the simulation. It generates vehicles behind a manually-created leading vehicle
        and populates the lane with vehicles based on the traffic model.
        
        Parameter ``leader``:
            The manually-created leader vehicle.
        
        Returns:
            A vector of pointers to the created vehicles.
        """
    def validate_creator(self) -> None:
        """
        Validates the configuration of the creator.
        
        This method validates the configurations of the creator, such as ensuring that
        the maximum number of vehicles and the model are properly set. This ensures that
        vehicle creation follows the expected limits and behavior.
        """
class CreatorMartinezJin2020(Creator):
    """
    Vehicle creator based on the Martinez and Jin (2020) model, with random jam
    density.
    
    The `creator_martinez_jin_2020` class generates vehicles according to the
    Martinez and Jin (2020) car-following model, with random variations in jam
    density. Vehicles are placed in a lane with a given spacing and initial speed,
    unless constrained by the lane's capacity or other vehicles.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, model_params: p_martinez_jin_2020, spacing: float, speed: float) -> None:
        """
        Constructs a vehicle creator with the Martinez and Jin model.
        
        This constructor creates a vehicle creator that generates vehicles with a fixed
        spacing and initial speed. Jam density is randomly generated within a defined
        range.
        
        Parameter ``model_params``:
            Parameters for the Martinez and Jin model.
        
        Parameter ``spacing``:
            Desired spacing between vehicles.
        
        Parameter ``speed``:
            Initial speed for the created vehicles.
        """
    @typing.overload
    def __init__(self, model_params: p_martinez_jin_2020, spacing: float, speed: float, deviation: float, avg_jam_density: float) -> None:
        """
        Constructs a vehicle creator with the Martinez and Jin model and custom jam
        density range.
        
        This constructor creates a vehicle creator that generates vehicles with a fixed
        spacing and initial speed. Jam density is randomly generated within the
        specified range.
        
        Parameter ``model_params``:
            Parameters for the Martinez and Jin model.
        
        Parameter ``spacing``:
            Desired spacing between vehicles.
        
        Parameter ``speed``:
            Initial speed for the created vehicles.
        
        Parameter ``deviation``:
            Maximum percentage deviation for the random jam density.
        
        Parameter ``avg_jam_density``:
            Average jam density.
        """
    @typing.overload
    def __init__(self, model_params: p_martinez_jin_2020, spacing: float, speed: float, max_vehicles: int) -> None:
        """
        Constructs a vehicle creator with a limit on the number of vehicles.
        
        This constructor creates a vehicle creator that generates vehicles with a fixed
        spacing and initial speed, up to a maximum number of vehicles.
        
        Parameter ``model_params``:
            Parameters for the Martinez and Jin model.
        
        Parameter ``spacing``:
            Desired spacing between vehicles.
        
        Parameter ``speed``:
            Initial speed for the created vehicles.
        
        Parameter ``max_vehicles``:
            Maximum number of vehicles to be created.
        """
    @typing.overload
    def __init__(self, model_params: p_martinez_jin_2020, spacing: float, speed: float, deviation: float, avg_jam_density: float, max_vehicles: int) -> None:
        """
        Constructs a vehicle creator with a custom jam density range and vehicle limit.
        
        This constructor creates a vehicle creator that generates vehicles with a fixed
        spacing and initial speed, with a random jam density and a limit on the total
        number of vehicles created.
        
        Parameter ``model_params``:
            Parameters for the Martinez and Jin model.
        
        Parameter ``spacing``:
            Desired spacing between vehicles.
        
        Parameter ``speed``:
            Initial speed for the created vehicles.
        
        Parameter ``deviation``:
            Maximum percentage deviation for the random jam density.
        
        Parameter ``avg_jam_density``:
            Average jam density.
        
        Parameter ``max_vehicles``:
            Maximum number of vehicles to be created.
        """
    def create(self, leader: Point, immediate_follower: bool = False) -> Vehicle:
        """
        Creates a vehicle with random jam density behind a leader.
        
        This method checks whether it is possible to create a vehicle based on the
        leader's current state. If allowed, it creates a new vehicle using the Martinez
        and Jin model with random jam density.
        
        Parameter ``leader``:
            The current point of the leader vehicle.
        
        Parameter ``immediate_follower``:
            If `true`, the new vehicle is placed just behind the leader.
        
        Returns:
            A pointer to the created vehicle, or `nullptr` if no vehicle was created.
        """
    def create_no_leader(self, lane: int) -> Vehicle:
        """
        Creates a vehicle in an empty lane with random jam density.
        
        This method generates a vehicle at the start of an empty lane using the Martinez
        and Jin model with random jam density.
        
        Parameter ``lane``:
            The lane number where the vehicle is created.
        
        Returns:
            A pointer to the created vehicle, or `nullptr` if no vehicle was created.
        """
    def validate_creator(self) -> None:
        """
        Validates the parameters of the Martinez and Jin model.
        
        This method ensures that the parameters of the Martinez and Jin model are valid
        and feasible for the simulation.
        """
class CustomModelBuilder:
    """
    Fluent builder for `accurate_custom_model`.
    
    This class provides a user-friendly interface for constructing a custom model
    without subclassing or manual memory management. All functions must be set
    before calling `build()`. Callbacks are passed using lambdas or function
    pointers.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        ...
    def build(self) -> accurate_custom_model:
        """
        Build the `accurate_custom_model` instance.
        
        Returns:
            A pointer to the constructed model.
        
        Throws:
            Exception if any required components are missing.
        """
    def set_accel(self, callback: typing.Callable[[ModelContext], float]) -> CustomModelBuilder:
        """
        Set the acceleration behavior function.
        
        Parameter ``cb``:
            Callback taking a `ModelContext` and returning acceleration (m/s²).
        
        Returns:
            Reference to this builder.
        """
    def set_free_flow(self, callback: typing.Callable[[ModelContext], float]) -> CustomModelBuilder:
        """
        Set the free-flow speed function.
        
        Parameter ``cb``:
            Callback taking a `ModelContext` (with only `p`) and returning free-flow
            speed (m/s).
        
        Returns:
            Reference to this builder.
        """
    def set_params(self, p: params_cust) -> CustomModelBuilder:
        """
        Set the custom parameter set used by the model.
        
        Parameter ``p``:
            An instance of `params_cust` with all needed key-value pairs.
        
        Returns:
            Reference to this builder.
        """
    def set_spacing(self, callback: typing.Callable[[ModelContext], float]) -> CustomModelBuilder:
        """
        Set the spacing function.
        
        Parameter ``cb``:
            Callback taking a `ModelContext` (with velocity fields) and returning
            spacing (m).
        
        Returns:
            Reference to this builder.
        """
    def set_wave_speed(self, callback: typing.Callable[[ModelContext], float]) -> CustomModelBuilder:
        """
        Set the wave speed function.
        
        Parameter ``cb``:
            Callback taking a `ModelContext` and returning wave speed (m/s).
        
        Returns:
            Reference to this builder.
        """
class DistributionType:
    """
    
    
    Members:
    
      Normal : 
    
      Logistic : 
    
      LogNormal : 
    
      Uniform : 
    """
    LogNormal: typing.ClassVar[DistributionType]  # value = <DistributionType.LogNormal: 3>
    Logistic: typing.ClassVar[DistributionType]  # value = <DistributionType.Logistic: 1>
    Normal: typing.ClassVar[DistributionType]  # value = <DistributionType.Normal: 0>
    Uniform: typing.ClassVar[DistributionType]  # value = <DistributionType.Uniform: 7>
    __members__: typing.ClassVar[dict[str, DistributionType]]  # value = {'Normal': <DistributionType.Normal: 0>, 'Logistic': <DistributionType.Logistic: 1>, 'LogNormal': <DistributionType.LogNormal: 3>, 'Uniform': <DistributionType.Uniform: 7>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class FixedDemandCreator(Creator):
    """
    Vehicle creator that injects vehicles at a fixed rate (flow).
    
    The `fixed_demand_creator` class generates vehicles based on a specified flow
    rate, placing them at the beginning of a lane or behind a leader. Vehicles are
    injected at regular intervals based on the desired headway.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, model: model, flow: float) -> None:
        """
        Constructs a fixed-demand vehicle creator.
        
        This constructor creates a vehicle creator that generates vehicles at a
        specified flow rate.
        
        Parameter ``model``:
            A car-following model governing the lane's capacity.
        
        Parameter ``flow``:
            The target flow rate (vehicles per second).
        """
    @typing.overload
    def __init__(self, model: model, flow: float, max_vehicles: int) -> None:
        """
        Constructs a limited fixed-demand vehicle creator.
        
        This constructor creates a vehicle creator that generates vehicles at a
        specified flow rate with a limit on the maximum number of vehicles created.
        
        Parameter ``model``:
            A car-following model governing the lane's capacity.
        
        Parameter ``flow``:
            The target flow rate (vehicles per second).
        
        Parameter ``max_vehicles``:
            The maximum number of vehicles to create.
        """
    def create_no_leader(self, lane: int) -> Vehicle:
        """
        Creates a new vehicle in a lane without a leader.
        
        This function generates a new vehicle in an empty lane if there is space, or
        returns `nullptr` if no more vehicles can be created.
        
        Parameter ``lane``:
            The lane number where the vehicle is created.
        
        Returns:
            A pointer to the created vehicle, or `nullptr` if no vehicle was created.
        """
    def validate_creator(self) -> None:
        """
        Validates the flow rate parameters of the fixed-demand vehicle creator.
        
        This method checks that the specified flow rate is feasible given the time step
        (`dt`) of the simulation. If the demand is not feasible, an exception will be
        thrown.
        """
class FixedObject(RoadObject):
    """
    Class representing a fixed object on the road.
    
    The `FixedObject` class models a static object on the road, such as a roadblock
    or a parked vehicle. It remains stationary and has a fixed position in the
    simulation.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, pos: Point) -> None:
        """
        Constructor for the `FixedObject` class.
        
        Initializes the object with a fixed position on the road.
        
        Parameter ``pos``:
            A pointer to the position of the object.
        """
    def current(self) -> Point:
        """
        Get the current position of the fixed object.
        
        Since the object is fixed, this method always returns the same position.
        
        Returns:
            A pointer to the object's current position.
        """
    def update(self, ro: RoadObject) -> None:
        """
        Update the state of the fixed object.
        
        Since the object is fixed, this method does nothing. It is provided to satisfy
        the interface.
        
        Parameter ``ro``:
            A pointer to another road object (unused in this context).
        """
class FixedStateCreator(Creator):
    """
    Vehicle creator that injects vehicles with a fixed state (spacing and speed).
    
    The `FixedStateCreator` class generates vehicles based on a specified spacing
    and initial speed. Vehicles are placed at the start of the lane, or just behind
    a leader, if a leader vehicle is present. This class is typically used for
    scenarios where vehicles need to maintain a fixed headway and speed.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, model: model, spacing: float, speed: float) -> None:
        """
        Constructs a fixed-state vehicle creator.
        
        This constructor creates a vehicle creator with specified model, spacing, and
        initial speed. It also allows limiting the maximum number of vehicles to be
        created.
        
        Parameter ``model``:
            A car-following model governing the lane's capacity.
        
        Parameter ``spacing``:
            Target spacing between vehicles.
        
        Parameter ``speed``:
            Initial speed for the created vehicles.
        
        Parameter ``max_vehicles``:
            Maximum number of vehicles to create.
        """
    @typing.overload
    def __init__(self, model: model, spacing: float, speed: float, max_vehicles: int) -> None:
        """
        Constructs a fixed-state vehicle creator.
        
        This constructor creates a vehicle creator with specified model, spacing, and
        initial speed.
        
        Parameter ``model``:
            A car-following model governing the lane's capacity.
        
        Parameter ``spacing``:
            Target spacing between vehicles.
        
        Parameter ``speed``:
            Initial speed for the created vehicles.
        """
    def create_no_leader(self, lane: int) -> Vehicle:
        """
        Creates a new vehicle in a lane without a leader.
        
        This function generates a new vehicle in an empty lane if there is space, or
        returns `nullptr` if no more vehicles can be created.
        
        Parameter ``lane``:
            The lane number where the vehicle is created.
        
        Returns:
            A pointer to the created vehicle, or `nullptr` if no vehicle was created.
        """
    def validate_creator(self) -> None:
        """
        Validates the parameters of the fixed-state vehicle creator.
        
        Ensures that the model parameters are valid and the spacing is appropriate for
        the simulation. If the parameters are invalid, an error will be thrown.
        """
class GeneralizedTrajectory:
    """
    Base class for different types of trajectories.
    
    This class provides an interface for retrieving points in a trajectory. Both
    `trajectory` and `static_trajectory` classes inherit from this class.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __getitem__(self, index: int) -> Point:
        """
        Get a point by integer index.
        
        Parameter ``index``:
            Integer index of the point.
        
        Returns:
            Pointer to the point at the specified index.
        """
    @typing.overload
    def __getitem__(self, index: float) -> Point:
        """
        Get a point by interpolating a floating-point index.
        
        Parameter ``index``:
            Floating-point index of the point.
        
        Returns:
            Pointer to the interpolated point.
        """
    def get_current_point(self) -> Point:
        """
        Get the current point of the trajectory.
        
        Returns:
            Pointer to the current point.
        """
class Geometry:
    """
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, length: float, initial_lanes: int, merge_positions: list[float] = [], diverge_positions: list[float] = []) -> None:
        """
        Constructs a `Geometry` object with specified physical properties.
        
        Validates that the highway length and initial lanes are positive. Checks that
        merge and diverge positions are within the highway’s bounds and sorted in
        ascending order. Ensures that merges do not reduce lanes below one, and that
        diverges do not unrealistically increase lane count.
        
        Parameter ``length``:
            Length of the highway segment in meters.
        
        Parameter ``initial_lanes``:
            Initial number of lanes at the start of the segment.
        
        Parameter ``merge_positions``:
            Positions where lanes merge (sorted in ascending order).
        
        Parameter ``diverge_positions``:
            Positions where lanes diverge (sorted in ascending order).
        
        Throws:
            Exception if any of the input parameters are invalid.
        """
    @typing.overload
    def __init__(self, length: float, initial_lanes: int, merge_position: float, diverge_position: float) -> None:
        """
        Constructs a `Geometry` object with specified physical properties.
        
        Parameter ``length``:
            Length of the highway segment in meters.
        
        Parameter ``initial_lanes``:
            Initial number of lanes at the start of the segment.
        
        Parameter ``merge_position``:
            Position where lanes merge.
        
        Parameter ``diverge_position``:
            Positions where lanes diverge.
        
        Throws:
            Exception if any of the input parameters are invalid.
        """
    @typing.overload
    def __init__(self, length: float, initial_lanes: int, merge_positions: list[float], diverge_position: float) -> None:
        """
        Constructs a `Geometry` object with specified physical properties.
        
        Parameter ``length``:
            Length of the highway segment in meters.
        
        Parameter ``initial_lanes``:
            Initial number of lanes at the start of the segment.
        
        Parameter ``merge_positions``:
            Positions where lanes merge (sorted in ascending order).
        
        Parameter ``diverge_position``:
            Position where a the lanes diverge.
        
        Throws:
            Exception if any of the input parameters are invalid.
        """
    @typing.overload
    def __init__(self, length: float, initial_lanes: int, merge_position: float, diverge_positions: list[float]) -> None:
        """
        Constructs a `Geometry` object with specified physical properties.
        
        Parameter ``length``:
            Length of the highway segment in meters.
        
        Parameter ``initial_lanes``:
            Initial number of lanes at the start of the segment.
        
        Parameter ``merge_position``:
            Position where lanes merge.
        
        Parameter ``diverge_positions``:
            Positions where a the lanes diverge (sorted in ascending order).
        
        Throws:
            Exception if any of the input parameters are invalid.
        """
    @typing.overload
    def __init__(self, length: float, lanes: int) -> None:
        """
        Constructs a `Geometry` object with minimal properties (no ramps).
        
        Parameter ``length``:
            Length of the highway segment in meters.
        
        Parameter ``lanes``:
            Number of lanes.
        """
    def can_change_left(self, point: Point) -> bool:
        """
        Checks if a vehicle can change lanes to the left.
        
        Parameter ``point``:
            Pointer to the current position of the vehicle.
        
        Returns:
            `true` if a left lane change is allowed, `false` otherwise.
        """
    def can_change_right(self, point: Point) -> bool:
        """
        Checks if a vehicle can change lanes to the right.
        
        Parameter ``point``:
            Pointer to the current position of the vehicle.
        
        Returns:
            `true` if a right lane change is allowed, `false` otherwise.
        """
    def get_current_lanes(self, position: float) -> int:
        """
        Returns the current number of lanes based on a given position.
        
        Parameter ``position``:
            The position along the highway segment in meters.
        
        Returns:
            The current number of lanes.
        """
    def get_diverge_positions(self) -> list[float]:
        """
        Returns the diverge positions along the highway.
        
        Returns:
            A vector of diverge positions in meters.
        """
    def get_highway_shape(self) -> str:
        """
        Returns a string that represents the structure of the highway for debugging
        purposes.
        
        Returns:
            The string that represents the highway, including merges and diverges.
        """
    def get_initial_lanes(self) -> int:
        """
        Returns the initial number of lanes on the highway.
        
        Returns:
            The total number of lanes (excluding on/off-ramps).
        """
    def get_length(self) -> float:
        """
        Returns the total length of the highway segment.
        
        Returns:
            The length of the highway in meters.
        """
    def get_max_lanes(self) -> int:
        """
        Returns the max amount of lanes on the highway
        
        Returns:
            returns max_lanes which includes the ammount of merges and diverges
        """
    def get_merge_positions(self) -> list[float]:
        """
        Returns the merge positions along the highway.
        
        Returns:
            A vector of merge positions in meters.
        """
    def has_diverge(self) -> bool:
        """
        Checks if the highway segment has an off-ramp (diverge).
        
        Returns:
            `true` if there is an off-ramp, `false` otherwise.
        """
    def has_merge(self) -> bool:
        """
        Checks if the highway segment has an on-ramp (merge).
        
        Returns:
            `true` if there is an on-ramp, `false` otherwise.
        """
class LCM:
    """
    Abstract class for lane-changing models.
    
    This class handles the logic for determining whether a vehicle should change
    lanes based on its current state, the state of nearby vehicles, and model-
    specific parameters.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class ModelContext:
    """
    Unified context passed to all user-defined behavior functions.
    
    This context is shared across all components (accel, spacing, wave speed, free-
    flow). It wraps the state of the leader and follower vehicles (if applicable)
    and provides access to user-defined model parameters.
    
    For spacing and free-flow computations, additional fields `v_leader` and
    `v_follower` are used to supply velocities when vehicle pointers are not
    relevant.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __repr__(self) -> str:
        ...
    def has_follower(self) -> bool:
        """
        Returns True if a follower vehicle is present in the context.
        """
    def has_leader(self) -> bool:
        """
        Returns True if a leader vehicle is present in the context.
        """
    @property
    def follower(self) -> Point:
        """
        Pointer to the follower vehicle (or None if not available).
        Use `has_follower()` to check for presence.
        """
    @property
    def leader(self) -> Point:
        """
        Pointer to the leader vehicle (or None if not available).
        Use `has_leader()` to check for presence.
        """
    @property
    def params(self) -> params_cust:
        """
        Model parameters (custom key-value mapping).
        """
    @property
    def v_follower(self) -> float:
        """
        Velocity of the follower (used in spacing context).
        May be NaN if not applicable.
        """
    @property
    def v_leader(self) -> float:
        """
        Velocity of the leader (used in spacing context).
        May be NaN if not applicable.
        """
class MultiModelDemandCreator(Creator):
    """
    Vehicle creator that randomly selects a model from a set (with weights) to
    generate vehicles at a fixed flow rate.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, models: dict[model, float], flow: float) -> None:
        """
        Constructs a multi-model demand creator.
        
        Parameter ``models``:
            Unordered map of Model pointers and their corresponding weights.
        
        Parameter ``flow``:
            Target flow rate (vehicles per second).
        """
    @typing.overload
    def __init__(self, models: dict[model, float], flow: float, max_vehicles: int) -> None:
        """
        Constructs a multi-model demand creator with a vehicle creation limit.
        
        Parameter ``models``:
            Unordered map of Model pointers and their corresponding weights.
        
        Parameter ``flow``:
            Target flow rate.
        
        Parameter ``max_vehicles``:
            Maximum number of vehicles to create.
        """
    def create(self, leader: Point, immediate_follower: bool = False) -> Vehicle:
        """
        Creates a new vehicle behind a leader.
        
        Parameter ``leader``:
            Pointer to the leader's state.
        
        Parameter ``immediate_follower``:
            Whether the vehicle is an immediate follower.
        
        Returns:
            Pointer to the created vehicle, or nullptr if not possible.
        """
    def create_no_leader(self, lane: int) -> Vehicle:
        """
        Creates a new vehicle in an empty lane.
        
        Parameter ``lane``:
            The lane number where the vehicle is created.
        
        Returns:
            Pointer to the new vehicle, or nullptr if creation is not possible.
        """
    def validate_creator(self) -> None:
        """
        Validates that the flow rate is feasible and all models are properly configured.
        """
class MultiModelStateCreator(Creator):
    """
    Vehicle creator that randomly selects a model to generate vehicles with fixed
    spacing and initial speed.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, models: dict[model, float], spacing: float, speed: float) -> None:
        """
        Constructs a multi-model state creator.
        
        Parameter ``models``:
            Unordered map of models and their weights.
        
        Parameter ``spacing``:
            Target spacing between vehicles.
        
        Parameter ``speed``:
            Initial speed for the vehicles.
        
        Throws:
            Exception if spacing is nonpositive or less than any model's jam spacing.
        """
    @typing.overload
    def __init__(self, models: dict[model, float], spacing: float, speed: float, max_vehicles: int) -> None:
        """
        Constructs a multi-model state creator with a limit on vehicle creation.
        
        Parameter ``models``:
            Unordered map of models and weights.
        
        Parameter ``spacing``:
            Target spacing.
        
        Parameter ``speed``:
            Initial speed.
        
        Parameter ``max_vehicles``:
            Maximum number of vehicles to create.
        """
    def create(self, leader: Point, immediate_follower: bool = False) -> Vehicle:
        """
        Creates a new vehicle behind a leader.
        
        Parameter ``leader``:
            Pointer to the leader's state.
        
        Parameter ``immediate_follower``:
            Whether the vehicle is an immediate follower.
        
        Returns:
            Pointer to the created vehicle, or nullptr if creation is not possible.
        """
    def create_no_leader(self, lane: int) -> Vehicle:
        """
        Creates a new vehicle in an empty lane.
        
        Parameter ``lane``:
            The lane number for the new vehicle.
        
        Returns:
            Pointer to the new vehicle, or nullptr if the limit is reached.
        """
    def validate_creator(self) -> None:
        """
        Validates that each model is properly configured.
        """
class Point:
    """
    Represents a point in time for a vehicle in a traffic simulation.
    
    The point class stores and manages the time, position, velocity, acceleration,
    and lane of a vehicle during simulation.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def A(self) -> float:
        """
        Gets the acceleration value.
        
        Returns:
            Current acceleration value.
        """
    def LANE(self) -> int:
        """
        Gets the lane value.
        
        Returns:
            Current lane value.
        """
    def T(self) -> float:
        """
        Gets the time value.
        
        Returns:
            Current time value.
        """
    def V(self) -> float:
        """
        Gets the velocity value.
        
        Returns:
            Current velocity value.
        """
    def X(self) -> float:
        """
        Gets the position value.
        
        Returns:
            Current position value.
        """
    def __eq__(self, arg0: Point) -> bool:
        ...
    @typing.overload
    def __init__(self, time: float = 0.0, position: float = 0.0, velocity: float = 0.0, acceleration: float = 0.0, lane: int = 0) -> None:
        """
        Constructor for the Point class.
        
        Initializes the Point object with specified time, position, velocity,
        acceleration, and lane.
        
        Parameter ``time``:
            Initial time.
        
        Parameter ``position``:
            Initial position.
        
        Parameter ``velocity``:
            Initial velocity.
        
        Parameter ``acceleration``:
            Initial acceleration.
        
        Parameter ``lane``:
            Initial lane.
        """
    @typing.overload
    def __init__(self, arg0: Point) -> None:
        """
        Copy constructor for the Point class.
        
        Creates a new Point object by copying values from another Point object.
        
        Parameter ``other``:
            Point object to duplicate.
        """
    def reset_time(self) -> None:
        """
        Resets the time of the point to zero.
        
        This function resets the time value of the point object to zero.
        """
    def set_accel(self, acceleration: float) -> None:
        """
        Sets the acceleration of the point.
        
        Parameter ``newAcceleration``:
            New acceleration value.
        """
    def set_lane(self, lane: int) -> None:
        """
        Sets the lane of the point.
        
        Parameter ``newLane``:
            New lane value.
        """
    def set_velocity(self, velocity: float) -> None:
        """
        Sets the velocity of the point.
        
        Parameter ``newVelocity``:
            New velocity value.
        """
    def set_x(self, position: float) -> None:
        """
        Sets the position of the point.
        
        Parameter ``newPosition``:
            New position value.
        """
    def to_string(self) -> str:
        """
        Converts the Point object to a string representation.
        
        This function generates a string that represents the current state of the Point
        object.
        
        Returns:
            A string representing the Point object.
        """
class RandomGenerator:
    """
    Utility class for generating random numbers using various distributions.
    
    `RandomGenerator` provides static methods for generating random values from: -
    Uniform distributions ([0,1] or [a,b]) - Normal (Gaussian) distribution -
    Logistic distribution
    
    The class uses a Mersenne Twister engine to produce high-quality random numbers.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def generate_seed() -> int:
        """
        Generates a high-entropy random seed for random number generation.
        
        This function combines entropy from multiple sources to produce a robust seed
        value. It uses a combination of: - A hardware-based random number generator
        (`std::random_device`), which provides non-deterministic random values, when
        available. - The current high-resolution system clock
        (`std::chrono::high_resolution_clock`), which adds a time-dependent component to
        the seed, ensuring uniqueness across successive calls within short time
        intervals. - A uniform random distribution (`std::uniform_int_distribution`) to
        map the random device output into the full range of `unsigned long`.
        
        These components are XOR-combined to enhance the randomness and reduce the
        likelihood of predictable or repeating seed values, especially in environments
        with limited entropy.
        
        This method ensures a high level of randomness suitable for seeding pseudo-
        random number generators (PRNGs) in simulation, where randomness quality is
        crucial.
        
        Returns:
            An unsigned long value representing the generated random seed.
        
        @note This function relies on both hardware and software entropy sources. If
        `std::random_device` is deterministic on your platform, the generated seed may
        have reduced randomness.
        
        See also:
            std::random_device
        
        See also:
            std::chrono::high_resolution_clock
        
        See also:
            std::uniform_int_distribution
        """
    @staticmethod
    def init(seed: int) -> None:
        """
        Initialize the random number generator with a seed.
        
        This method initializes the Mersenne Twister generator using the current time as
        the seed. This ensures that the generator produces different random sequences
        each time the program runs.
        
        Parameter ``seed``:
            Optional seed for the random generator. Uses current time if not provided.
        """
    @staticmethod
    def logistic(location: float = 0.0, scale: float = 1.0) -> float:
        """
        Generate a random value from a logistic distribution.
        
        This method returns a random value sampled from a logistic distribution with
        location `mu` and scale `s`. The logistic distribution is commonly used in
        various models, including machine learning and statistics.
        
        Parameter ``mu``:
            The location parameter of the logistic distribution (mean).
        
        Parameter ``s``:
            The scale parameter (related to the standard deviation).
        
        Returns:
            A random double value sampled from a logistic distribution.
        """
    @staticmethod
    def normal(mean: float = 0.0, stddev: float = 1.0) -> float:
        """
        Generates a random value from a normal (Gaussian) distribution.
        
        Parameter ``mean``:
            The mean of the normal distribution.
        
        Parameter ``stddev``:
            The standard deviation of the normal distribution.
        
        Returns:
            A random double from the specified normal distribution.
        """
    @staticmethod
    def uniform(a: float = 0.0, b: float = 1.0) -> float:
        """
        Generate a random value from a uniform distribution [a, b].
        
        This method returns a random value sampled from a uniform distribution with
        bounds `a` and `b`.
        
        Parameter ``a``:
            The minimum value of the distribution.
        
        Parameter ``b``:
            The maximum value of the distribution.
        
        Returns:
            A random double value between `a` and `b`.
        """
    @staticmethod
    def uniform01() -> float:
        """
        Generate a random value from a standard uniform distribution [0, 1].
        
        This method returns a random value sampled from a uniform distribution between 0
        and 1.
        
        Returns:
            A random double value between 0 and 1.
        """
class Results:
    """
    The `results` class manages and processes simulation results.
    
    This class stores and organizes the trajectories of vehicles by lane, and
    provides methods to analyze the data, such as computing Edie's flow and density,
    or getting vehicle positions at specific times or distances.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, trajectories: list[Trajectory]) -> None:
        """
        Constructor that initializes the `results` object with a list of trajectories.
        
        Parameter ``trajectories``:
            A vector of trajectories from the simulation.
        """
    def calculate_edie(self, start_time: float, end_time: float, time_step: float, start_dist: float, end_dist: float, lane: int) -> list[list[float]]:
        """
        Computes Edie's flow and density for a specific time interval and distance.
        
        This method analyzes the Trajectory data to calculate flow and density values
        within a specified time-space region.
        
        Parameter ``start_time``:
            Start time.
        
        Parameter ``end_time``:
            End time.
        
        Parameter ``time_step``:
            Time step size.
        
        Parameter ``start_dist``:
            Start distance.
        
        Parameter ``end_dist``:
            End distance.
        
        Parameter ``lane``:
            Lane number.
        
        Returns:
            A vector of vectors containing the computed flow and density values.
        """
    def get_all_trajectories(self) -> list[Trajectory]:
        """
        Gets all vehicle trajectories.
        
        Returns:
            A vector containing the trajectories of all vehicles.
        """
    def get_all_trajectories_by_lane(self) -> list[Trajectory]:
        """
        Retrieves all trajectories across all lanes.
        
        Returns:
            A vector containing all trajectories in the simulation.
        """
    def get_trajectories_by_lane(self, lane: int) -> list[Trajectory]:
        """
        Retrieves all trajectories in a specific lane.
        
        Parameter ``lane``:
            Lane number.
        
        Returns:
            A vector of trajectories in the specified lane.
        """
    def get_trajectories_by_vehicle(self, vehicle_index: int) -> list[Trajectory]:
        """
        Splits a vehicle's Trajectory by lane.
        
        This method processes the Trajectory of a specific vehicle and splits it into
        separate trajectories based on lane changes.
        
        Parameter ``vehicle_index``:
            Index of the vehicle Trajectory.
        
        Returns:
            A vector of trajectories split by lane.
        """
    def get_trajectory(self, index: int) -> Trajectory:
        ...
    def passes_on_t(self, time: float, lane: int) -> list[Point]:
        """
        Retrieves the list of points where vehicles pass at a specific time in a given
        lane.
        
        Parameter ``time``:
            The time at which to check vehicle positions.
        
        Parameter ``lane``:
            The lane number.
        
        Returns:
            A vector of points representing vehicle positions at the specified time and
            lane.
        """
    def passes_on_x(self, position: float, lane: int) -> list[Point]:
        """
        Retrieves the list of points where vehicles pass at a specific distance in a
        given lane.
        
        Parameter ``position``:
            The distance at which to check vehicle positions.
        
        Parameter ``lane``:
            The lane number.
        
        Returns:
            A vector of points representing vehicle positions at the specified distance
            and lane.
        """
    def plot_3d_x_t_lane(self) -> None:
        """
        Plot a 3D graph of Time vs Position vs Lane.
        """
    def plot_v_vs_t(self, lane: int = -1) -> None:
        """
        Plot velocities (velocity vs time) for all or a specific lane.
        """
    def plot_x_vs_t(self, lane: int = -1) -> None:
        """
        Plot trajectories (position vs time) for all or a specific lane.
        """
class RoadObject:
    """
    Abstract base class representing any object on the road.
    
    The `RoadObject` class serves as a general interface for objects on the road,
    whether they are moving vehicles or fixed objects. It handles the object's
    trajectory and allows updating based on interactions with other road objects.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def current(self) -> Point:
        """
        Get the current point of the object.
        
        This pure virtual function must be implemented by derived classes to return the
        object's current position and state.
        
        Returns:
            A pointer to the current point representing the object's state.
        """
    def update(self, leader: RoadObject) -> None:
        """
        Update the object's state based on another road object.
        
        This pure virtual function must be implemented by derived classes. It updates
        the object’s state, such as position and speed, possibly considering the
        position of a leader or other objects on the road.
        
        Parameter ``leader``:
            A pointer to the road object that may influence this object’s state.
        """
    @property
    def trajectory(self) -> GeneralizedTrajectory:
        """
        Object's trajectory, which defines its movement and positions over time.
        """
    @trajectory.setter
    def trajectory(self, arg0: GeneralizedTrajectory) -> None:
        ...
class Simulation:
    """
    The `simulation` class manages a traffic simulation over time.
    
    This class controls the creation of vehicles, their movement, lane changes, and
    interactions on a highway-like scenario. It updates vehicle states in discrete
    time steps.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __del__(self) -> None:
        """
        Destructor
        """
    @typing.overload
    def __init__(self, lane_change_model: LCM, total_time: float, geometry: Geometry, creator: Creator, time_step: float, verbose: bool = False) -> None:
        """
        Constructs a simulation with a common creator for all lanes.
        
        Parameter ``lane_change_model``:
            Lane-changing model.
        
        Parameter ``total_time``:
            Total simulation time.
        
        Parameter ``geometry``:
            Highway geometry.
        
        Parameter ``creator``:
            Vehicle creator for all lanes.
        
        Parameter ``time_step``:
            Time step for the simulation.
        
        Parameter ``verbose``:
            flag to enable verbose mode that prints some aditional info
        """
    @typing.overload
    def __init__(self, lane_change_model: LCM, total_time: float, geometry: Geometry, creators: list[Creator], vehicle: Vehicle, time_step: float, verbose: bool = False) -> None:
        """
        Constructs a simulation with specific creators for each lane.
        
        Parameter ``lane_change_model``:
            Lane-changing model.
        
        Parameter ``total_time``:
            Total simulation time.
        
        Parameter ``geometry``:
            Highway geometry.
        
        Parameter ``creators``:
            Vector of vehicle creators for each lane.
        
        Parameter ``vehicle``:
            A specific vehicle to insert into the simulation.
        
        Parameter ``time_step``:
            Time step for the simulation.
        
        Parameter ``verbose``:
            flag to enable verbose mode that prints some aditional info
        """
    @typing.overload
    def __init__(self, lane_change_model: LCM, total_time: float, geometry: Geometry, lane_creators: list[Creator], vehicles: list[Vehicle], time_step: float, verbose: bool = False) -> None:
        """
        Constructs a simulation with specific creators and vehicles.
        
        Parameter ``lane_change_model``:
            Lane-changing model.
        
        Parameter ``total_time``:
            Total simulation time.
        
        Parameter ``geometry``:
            Highway geometry.
        
        Parameter ``creators``:
            Vector of vehicle creators for each lane.
        
        Parameter ``vehicles``:
            Vector of pre-existing vehicles to insert into the simulation.
        
        Parameter ``time_step``:
            Time step for the simulation.
        
        Parameter ``verbose``:
            Flag to enable verbose mode that prints some additional info.
        """
    def get_seed(self) -> int:
        """
        Get the current seed value.
        
        Returns:
            The seed used for the simulation.
        """
    def run(self) -> Results:
        """
        Runs the simulation.
        
        This method runs the simulation, advancing the simulation state step by step
        until completion.
        
        Returns:
            A pointer to a `results` object containing the simulation results.
        """
    def set_seed(self, seed: int) -> None:
        """
        Set the seed for the random number generator.
        
        Parameter ``new_seed``:
            The seed value to use.
        """
class SimulationBuilder:
    """
    A builder class for constructing a Simulation object with flexible
    configuration.
    
    This class provides a fluent interface for setting up various parameters and
    components required to initialize a `Simulation` instance.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        """
        Constructs a SimulationBuilder with default values.
        
        Initializes the builder with default parameters.
        """
    def add_lane_creator(self, creator: Creator) -> SimulationBuilder:
        """
        Adds a vehicle creator for a lane.
        
        Parameter ``creator``:
            Pointer to the Creator object for vehicle generation in a lane.
        
        Returns:
            Reference to the current builder object.
        """
    def add_lane_creators(self, creators: list[Creator]) -> SimulationBuilder:
        """
        Adds multiple lane creators at once.
        
        Parameter ``creators``:
            A vector of pointers to Creator objects.
        
        Returns:
            Reference to the current builder object.
        """
    def add_vehicles(self, vehicle: typing.Any) -> SimulationBuilder:
        """
        Adds an initial vehicle to the simulation.
        
        Parameter ``vehicle``:
            Pointer to the Vehicle object to be added.
        
        Returns:
            Reference to the current builder object.
        """
    def build(self) -> Simulation:
        """
        Constructs and returns a Simulation object.
        
        Validates the provided configuration and builds the Simulation instance.
        
        Returns:
            Pointer to the newly constructed Simulation object. The caller is
            responsible for managing the memory unless you wrap it in a smart pointer.
        
        Throws:
            Exception or std::runtime_error if required parameters are missing or
            invalid.
        """
    def reset(self) -> SimulationBuilder:
        """
        Clears or resets the builder to its default state.
        
        This allows re-using a single builder instance to build multiple Simulation
        objects.
        
        Returns:
            Reference to the current builder object.
        """
    def set_geometry(self, geom: Geometry) -> SimulationBuilder:
        """
        Sets the highway geometry.
        
        Parameter ``geom``:
            Pointer to the Geometry object representing the highway configuration.
        
        Returns:
            Reference to the current builder object.
        """
    def set_lane_change_model(self, model: LCM) -> SimulationBuilder:
        """
        Sets the lane change model.
        
        Parameter ``model``:
            Pointer to the lane change model (LCM) to be used.
        
        Returns:
            Reference to the current builder object.
        """
    def set_seed(self, new_seed: int) -> SimulationBuilder:
        """
        Sets a fixed seed for random number generation in the simulation.
        
        If this is not called, the simulation may use a default or random seed.
        
        Parameter ``new_seed``:
            The user-provided seed value.
        
        Returns:
            Reference to the current builder object.
        """
    def set_time_step(self, step: float) -> SimulationBuilder:
        """
        Sets the simulation time step.
        
        Parameter ``dt``:
            Time step for the simulation in seconds.
        
        Returns:
            Reference to the current builder object.
        """
    def set_total_time(self, time: float) -> SimulationBuilder:
        """
        Sets the total simulation time.
        
        Parameter ``time``:
            Total simulation time in seconds.
        
        Returns:
            Reference to the current builder object.
        """
    def set_verbose(self, verbosity: bool) -> SimulationBuilder:
        """
        Enables or disables verbose mode.
        
        Parameter ``verbosity``:
            Boolean flag to enable or disable verbose output.
        
        Returns:
            Reference to the current builder object.
        """
class StaticTrajectory(GeneralizedTrajectory):
    """
    Represents a static trajectory for a fixed object on the road.
    
    This class handles the trajectory of static objects (such as a fixed vehicle or
    roadblock).
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __getitem__(self, index: int) -> Point:
        """
        Retrieves the point by integer index (always returns the static position).
        
        Parameter ``index``:
            Unused index parameter.
        
        Returns:
            The current position.
        """
    @typing.overload
    def __getitem__(self, index: float) -> Point:
        """
        Retrieves the point by floating-point index (always returns the static
        position).
        
        Parameter ``index``:
            Unused index parameter.
        
        Returns:
            The current position.
        """
    def __init__(self, fixed_position: Point) -> None:
        """
        Constructs a static trajectory with a fixed position.
        
        Parameter ``fixed_position``:
            The position of the static object.
        """
    def __len__(self) -> int:
        """
        Return 1 since the trajectory is static.
        """
    def get_current_point(self) -> Point:
        """
        Returns the current position of the static object.
        
        Returns:
            The current position as a point.
        """
class StochasticDemandCreator(Creator):
    """
    Creator that generates vehicles using a stochastic demand-based model.
    
    This creator uses a prototype model and a set of parameter statistics to create
    a new, randomized model instance for each vehicle created in a lane with no
    leader.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, model: model, flow: float, stats: dict[str, tuple[float, float]], distribution: DistributionType = ...) -> None:
        """
        Constructs a stochastic demand creator.
        
        Parameter ``model``:
            Prototype model to clone.
        
        Parameter ``flow``:
            The target flow rate (vehicles per second).
        
        Parameter ``stats``:
            Parameter statistics for randomization.
        """
    @typing.overload
    def __init__(self, model: model, flow: float, max_vehicles: int, stats: dict[str, tuple[float, float]], distribution: DistributionType = ...) -> None:
        """
        Constructs a stochastic demand creator with a vehicle creation limit.
        
        Parameter ``model``:
            Prototype model to clone.
        
        Parameter ``flow``:
            The target flow rate (vehicles per second).
        
        Parameter ``max_vehicles``:
            Maximum number of vehicles to create.
        
        Parameter ``stats``:
            Parameter statistics for randomizing model parameters.
        """
    def create(self, leader: Point, immediate_follower: bool = False) -> Vehicle:
        """
        Creates a new vehicle behind a leader.
        
        Parameter ``leader``:
            Pointer to the leader's state.
        
        Parameter ``immediate_follower``:
            Whether the vehicle is an immediate follower.
        
        Returns:
            Pointer to the created vehicle, or nullptr if not possible.
        """
    def create_no_leader(self, lane: int) -> Vehicle:
        """
        Creates a new vehicle in a lane with no leader.
        
        Parameter ``lane``:
            Lane number where the vehicle is created.
        
        Returns:
            A pointer to the newly created Vehicle.
        """
    def validate_creator(self) -> None:
        ...
class StochasticStateCreator(Creator):
    """
    Creator that generates vehicles using a stochastic model.
    
    This creator uses a prototype model and a set of parameter statistics to create
    a new, randomized model instance for each vehicle. The ideal vehicle state is
    computed similar to FixedStateCreator, but each vehicle gets its own model
    instance.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, model: model, spacing: float, speed: float, stats: dict[str, tuple[float, float]], distribution: DistributionType = ...) -> None:
        """
        Constructs a stochastic creator.
        
        Parameter ``model``:
            Prototype model to clone.
        
        Parameter ``spacing``:
            Desired spacing.
        
        Parameter ``speed``:
            Initial speed.
        
        Parameter ``stats``:
            Statistics (mean and stddev) for randomizing model parameters.
        """
    @typing.overload
    def __init__(self, model: model, spacing: float, speed: float, max_vehicles: int, stats: dict[str, tuple[float, float]], distribution: DistributionType = ...) -> None:
        """
        Constructs a stochastic creator with a vehicle creation limit.
        
        Parameter ``model``:
            Prototype model to clone.
        
        Parameter ``spacing``:
            Desired spacing.
        
        Parameter ``speed``:
            Initial speed.
        
        Parameter ``max_vehicles``:
            Maximum number of vehicles to create.
        
        Parameter ``stats``:
            Statistics (mean and stddev) for randomizing model parameters.
        """
    def create(self, leader: Point, immediate_follower: bool = False) -> Vehicle:
        """
        Creates a new vehicle based on a leader’s state.
        
        Parameter ``leader``:
            The leader’s current state.
        
        Parameter ``immediate_follower``:
            Flag to indicate if the vehicle should be placed immediately behind the
            leader.
        
        Returns:
            A pointer to the newly created Vehicle.
        """
    def create_no_leader(self, lane: int) -> Vehicle:
        """
        Creates a new vehicle in a lane with no leader.
        
        Parameter ``lane``:
            Lane number where the vehicle is created.
        
        Returns:
            A pointer to the newly created Vehicle.
        """
    def validate_creator(self) -> None:
        ...
class Test:
    """
    A utility class that provides common testing functions.
    
    This class contains utility functions for common tasks like checking if a number
    falls within a range and checking the length of a vector. It is designed to be a
    lightweight helper for various validation tasks.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def length(vector: list[float], length: int) -> bool:
        """
        Check if a vector has a specific length.
        
        This method checks whether the size of the given vector matches the specified
        length. It is a templated function, allowing it to work with vectors containing
        any data type.
        
        Template parameter ``T``:
            The type of the elements in the vector.
        
        Template parameter ``A``:
            The allocator type for the vector (typically `std::allocator`).
        
        Parameter ``v``:
            The vector to be checked.
        
        Parameter ``l``:
            The required length of the vector.
        
        Returns:
            True if the vector size matches the specified length, false otherwise.
        """
    @staticmethod
    def range_inc(number: float, min: float, max: float) -> bool:
        """
        Check if a number is within an inclusive range.
        
        This method checks whether a given number lies between a minimum and a maximum
        value (both bounds inclusive).
        
        Parameter ``number``:
            The number to be checked.
        
        Parameter ``min``:
            The minimum allowable value.
        
        Parameter ``max``:
            The maximum allowable value.
        
        Returns:
            True if the number lies within the range, false otherwise.
        """
class Trajectory(GeneralizedTrajectory):
    """
    Represents a dynamic trajectory of a moving object.
    
    This class stores a series of `point` objects that define the trajectory of a
    moving vehicle. It allows retrieving points using integer or floating-point
    indices, and handles extrapolation for negative indices.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, starting_point: Point) -> None:
        """
        Constructs a trajectory with an initial starting point.
        
        Parameter ``starting_point``:
            Initial point of the trajectory.
        """
    def __len__(self) -> int:
        """
        Return the number of points in the trajectory.
        """
    def add_and_return(self, new_point: Point) -> Point:
        """
        Adds a point and returns it.
        
        Parameter ``new_point``:
            Pointer to the new point to add.
        
        Returns:
            The added point.
        """
    def get_current_point(self) -> Point:
        """
        Gets the current position of the vehicle in the trajectory.
        
        Returns:
            The current point.
        """
    def get_point_at(self, index: int) -> Point:
        """
        Retrieves a point at the specified index.
        
        Parameter ``index``:
            Index of the point to retrieve.
        
        Returns:
            Pointer to the point at the specified index.
        """
    def get_trajectory_length(self) -> int:
        """
        Returns the length of the trajectory.
        
        Returns:
            Number of points in the trajectory.
        """
    def push_back(self, point: Point) -> None:
        """
        Adds a point to the trajectory.
        
        Parameter ``point``:
            Pointer to the point to add.
        """
class Vehicle(RoadObject):
    """
    Class representing a moving vehicle on the road.
    
    The `vehicle` class models a moving vehicle, which can either follow a
    predefined trajectory or behave according to a dynamic model. It offers multiple
    constructors to accommodate different ways of specifying the vehicle’s movement,
    including position history, points, or models that dictate its behavior.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self, x: list[float], lane: int) -> None:
        """
        Create a vehicle with a predefined trajectory and a single lane.
        
        This constructor initializes a vehicle with a list of X positions and a single
        lane. It assumes that the positions are equally spaced in time, with a fixed
        delta time between points.
        
        Parameter ``x``:
            A vector of X positions representing the vehicle’s position over time.
        
        Parameter ``l``:
            The lane in which the vehicle is moving.
        """
    @typing.overload
    def __init__(self, x: list[float], lane: list[int]) -> None:
        """
        Create a vehicle with a predefined trajectory across multiple lanes.
        
        This constructor initializes a vehicle with a list of X positions and a list of
        lane positions. It assumes that the positions are equally spaced in time, with a
        fixed delta time between points.
        
        Parameter ``x``:
            A vector of X positions representing the vehicle’s position over time.
        
        Parameter ``l``:
            A vector of lane positions corresponding to each X position.
        
        Throws:
            Exception If the size of `x` and `l` do not match.
        """
    @typing.overload
    def __init__(self, p: list[Point]) -> None:
        """
        Create a vehicle with a predefined trajectory based on points.
        
        This constructor initializes a vehicle with a list of `point` objects that
        define its trajectory over time.
        
        Parameter ``p``:
            A vector of pointers to `point` objects representing the vehicle's
            trajectory.
        
        Throws:
            Exception If the size of the trajectory is too short.
        """
    @typing.overload
    def __init__(self, model: model, position: float, speed: float, lane: int) -> None:
        """
        Create a vehicle with a model, initial position, speed, and lane.
        
        This constructor initializes a vehicle with a dynamic model that dictates its
        behavior, along with its initial position, speed, and lane.
        
        Parameter ``model``:
            Pointer to the model that will describe the vehicle's behavior.
        
        Parameter ``position``:
            The initial position of the vehicle.
        
        Parameter ``speed``:
            The initial speed of the vehicle.
        
        Parameter ``lane``:
            The lane in which the vehicle starts.
        """
    @typing.overload
    def __init__(self, model: model, point: Point) -> None:
        """
        Create a vehicle with a model and a starting point.
        
        This constructor initializes a vehicle with a dynamic model and a starting
        point, which contains information about its position, speed, and lane.
        
        Parameter ``model``:
            Pointer to the model that will describe the vehicle's behavior.
        
        Parameter ``point``:
            Pointer to the initial point of the vehicle.
        """
    def current(self) -> Point:
        """
        Get the current point of the vehicle.
        
        This method returns the vehicle's current position and state based on its
        trajectory.
        
        Returns:
            A pointer to the current point.
        """
    def initialize_vehicle(self) -> None:
        """
        Initialize the vehicle’s trajectory with real points.
        
        This method initializes the placeholder points of a vehicle that was created
        with a predefined trajectory, replacing them with real points in the simulation.
        """
    def p(self) -> params:
        """
        Get the model parameters associated with the vehicle.
        
        Returns:
            A pointer to the model parameters (`params`).
        """
    @property
    def needs_initialization(self) -> bool:
        """
        Flag indicating if the vehicle requires initialization within the simulation.
        """
    @needs_initialization.setter
    def needs_initialization(self, arg0: bool) -> None:
        ...
    @property
    def placeholder_points(self) -> list[Point]:
        """
        A vector of placeholder points used before simulation starts.
        """
    @placeholder_points.setter
    def placeholder_points(self, arg0: list[Point]) -> None:
        ...
class accurate_custom_model(model):
    """
    Customizable car-following model with user-defined logic.
    
    This class extends the base `Model` interface and allows customization of key
    behavioral elements via function callbacks. These functions define: -
    Acceleration behavior - Equilibrium spacing - Backward wave speed - Free-flow
    speed
    
    These components are configured via a builder (see `CustomModelBuilder`) and
    passed to this model, avoiding the need for subclassing.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, accel_cb: typing.Callable[[ModelContext], float], spacing_cb: typing.Callable[[ModelContext], float] = None, wave_cb: typing.Callable[[ModelContext], float] = None, free_flow_cb: typing.Callable[[ModelContext], float] = None) -> None:
        """
        Constructor for the customizable car-following model.
        
        Parameter ``accel_cb``:
            Function to compute acceleration (required).
        
        Parameter ``spacing_cb``:
            Function to compute equilibrium spacing (optional).
        
        Parameter ``wave_cb``:
            Function to compute wave speed (optional).
        
        Parameter ``free_flow_cb``:
            Function to compute free-flow speed (optional).
        """
    def __repr__(self) -> str:
        ...
class example_car(model):
    """
    A simple car-following model with a predefined trajectory.
    
    The `example_car` class models vehicle behavior based on a predefined trajectory
    of points. This class demonstrates basic car-following dynamics by returning
    points sequentially from its trajectory.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, trajectory: list[Point]) -> None:
        """
        Constructor for the `example_car` model.
        
        Initializes the car with a predefined trajectory of points.
        
        Parameter ``t``:
            A vector of points representing the trajectory of the vehicle over time.
        """
    def __repr__(self) -> str:
        ...
class fast_custom_model(model):
    """
    A customizable car-following model.
    
    This class inherits from Model and allows the behavior of the model to be
    defined at runtime via string expressions. It uses an expression solver to
    evaluate the provided expressions based on a set of dynamic variables and user-
    defined parameters.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, accelExpr: str, equilSpcgExpr: str, waveSpeedExpr: str, freeFlowSpeedExpr: str, customParams: params_cust) -> None:
        """
        Constructs a fast_custom_model.
        
        Parameter ``accelExpr``:
            String expression for acceleration.
        
        Parameter ``equilSpcgExpr``:
            String expression for equilibrium spacing.
        
        Parameter ``waveSpeedExpr``:
            String expression for wave speed.
        
        Parameter ``freeFlowSpeedExpr``:
            String expression for free-flow speed.
        
        Parameter ``customParams``:
            Pointer to a params_cust object containing custom parameters.
        """
    def __repr__(self) -> str:
        ...
    def compile_model(self) -> None:
        """
        Compiles all expressions and finalizes model configuration.
        
        This method must be called after all constants and derived variables have been
        declared. If not called, any attempt to use the model will throw an exception.
        """
    def declare_constant(self, name: str, value: float) -> None:
        """
        Declares a constant for the internal solver.
        
        This method registers a constant with the solver.
        
        Parameter ``name``:
            The name of the constant.
        
        Parameter ``value``:
            The numeric value of the constant.
        """
    def declare_derived_variable(self, name: str, expression: str) -> None:
        """
        Declares a derived variable for the internal solver.
        
        This method registers a derived variable with the solver.
        
        Parameter ``name``:
            The name of the derived variable.
        
        Parameter ``expr``:
            The expression that defines the derived variable.
        """
class gipps(model):
    """
    Gipps car-following model (1981).
    
    This class implements the Gipps (1981) car-following model, which aims to
    simulate the behavior of vehicles in a traffic stream, particularly how a
    vehicle responds to the movement of the preceding vehicle. The model is based on
    realistic driver and vehicle behavior constraints such as maximum acceleration,
    braking, and desired speeds.
    
    The model introduces two main constraints: - A free acceleration component that
    limits acceleration as the vehicle approaches its desired speed. - A braking
    component that ensures the vehicle can safely stop if the vehicle ahead brakes
    suddenly.
    
    Reference: Gipps, P.G. (1981), "A Behavioural Car-Following Model for Computer
    Simulation", Transport Research Part B, Vol. 15, pp. 105-111.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the Gipps model.
        
        Initializes the model with default parameter values, including default values
        for maximum acceleration, braking, and reaction time.
        """
    @typing.overload
    def __init__(self, params: p_gipps) -> None:
        """
        Constructor with custom parameters for the Gipps model.
        
        Initializes the model with a custom set of parameters, allowing the simulation
        to represent different vehicle and driver behaviors.
        
        Parameter ``p``:
            A pointer to a p_gipps parameter class containing the custom parameters.
        """
    def __repr__(self) -> str:
        ...
class idm(model):
    """
    The Intelligent Driver Model (IDM) for car-following behavior.
    
    This class implements the IDM, a widely used microscopic traffic model for
    simulating car-following behavior. The model computes the acceleration of
    vehicles based on the distance to the leading vehicle, the relative velocity,
    and various model parameters.
    
    The IDM captures the transition between free-flow, congested traffic, and stop-
    and-go waves based on a nonlinear formulation of acceleration and braking.
    
    @note Reference: M. Treiber, A. Hennecke, and D. Helbing, "Congested traffic
    states in empirical observations and microscopic simulations," Phys. Rev. E, 62,
    1805 (2000).
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the IDM model.
        
        Initializes the IDM model with default parameters.
        """
    @typing.overload
    def __init__(self, params: p_idm) -> None:
        """
        Constructor for the IDM model with custom parameters.
        
        Initializes the IDM model with custom parameters specified in the `p_idm`
        parameter object.
        
        Parameter ``pars``:
            Pointer to the IDM-specific parameters.
        """
    def __repr__(self) -> str:
        ...
class laval(model):
    """
    Laval & Leclercq (2008) exact discrete car-following model.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, params: p_laval) -> None:
        ...
    def __repr__(self) -> str:
        ...
class lcm_force(LCM):
    """
    Force-based lane-changing model.
    
    This class implements a lane-changing decision mechanism where vehicles evaluate
    the net lateral force acting upon them. The model is grounded on the notion of
    two-dimensional (2D) interactions between vehicles, as presented in Delpiano et
    al. (2020). Instead of relying on discrete lane-change rules or gap acceptance
    thresholds used in 1D models (e.g., Gipps' model), the force-based approach
    computes a net lateral force that reflects the combination of:
    
    - A lane-centering force: This drives vehicles toward the center of their lane.
    - A repulsive force: Originating from the presence of neighboring vehicles in
    adjacent lanes, this force increases as the space gap (or lateral distance)
    decreases.
    
    A lane change is triggered if the net lateral force in the target lane is
    significantly less (i.e., more comfortable) than that in the current lane. This
    is done while also ensuring that safety conditions (for example, adequate gaps
    with respect to the new leader and follower) are met.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the force-based lane-changing model.
        
        Uses default parameters for the force-based model.
        """
    @typing.overload
    def __init__(self, p: p_lcm_force) -> None:
        """
        Constructor with custom force-based parameters.
        
        Parameter ``p``:
            Pointer to a custom set of lane-changing parameters (p_lcm_force).
        """
class lcm_gipps(LCM):
    """
    Lane-changing model based on the Gipps (1986) behavioral model.
    
    This class manages the functionality for vehicle lane-changing decisions,
    according to the rules defined by Gipps's model. Vehicles decide when to
    overtake or return to their original lane based on traffic conditions and the
    parameters from the `p_lcm_gipps` class.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the Gipps lane-changing model.
        
        Initializes the model with default parameters.
        """
    @typing.overload
    def __init__(self, p: p_lcm_gipps) -> None:
        """
        Constructor for the Gipps lane-changing model with custom parameters.
        
        Parameter ``p``:
            Custom lane-changing parameters.
        """
class lcm_laval(LCM):
    """
    Laval & Leclercq (2008) stochastic lane-changing model.
    
    Implements the Laval & Leclercq lane-changing rule using a macroscopic flow-
    driven probability, where Φ is computed considering both demand/supply functions
    and the speed advantage from the target lane.
    
    The lane-changing decision is stochastic and performed at each simulation step
    via a Bernoulli trial with probability Φ·Δt.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor using Laval model defaults.
        """
    @typing.overload
    def __init__(self, p: p_lcm_laval) -> None:
        """
        Constructor with custom Laval lane-changing parameters.
        
        Parameter ``p``:
            Custom Laval LCM parameters.
        """
class linear(model):
    """
    Linear car-following model.
    
    The linear car-following model is a simple model that calculates the
    acceleration of a vehicle based on a linear function of the speed difference
    between the vehicle and the vehicle ahead (leader). It uses parameters such as
    free-flow speed, reaction time, and spacing to simulate vehicle behavior in
    traffic flow.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the linear model.
        
        Initializes the linear model with default parameter values.
        """
    @typing.overload
    def __init__(self, params: p_linear) -> None:
        """
        Constructor with custom parameters.
        
        Initializes the linear model with custom parameters provided via the p_linear
        class.
        
        Parameter ``p``:
            A pointer to the p_linear parameter object containing the model's
            parameters.
        """
    def __repr__(self) -> str:
        ...
class martinez_jin_2020(newell_constrained_timestep):
    """
    Martinez and Jin (2020) car-following model with constrained timestep.
    
    This class implements a stochastic car-following model based on the work of
    Martinez and Jin (2020), which extends Newell’s model by incorporating a wave
    travel time parameter (`tau`) and a stochastic jam density (`kj`). The model
    accounts for driver heterogeneity, allowing for the inclusion of both autonomous
    and human-driven vehicles with different dynamic behaviors.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the martinez_jin_2020 model.
        
        Initializes the model using default parameters from the p_martinez_jin_2020
        class.
        """
    @typing.overload
    def __init__(self, params: p_martinez_jin_2020) -> None:
        """
        Constructor with custom parameter values for the Martinez-Jin model.
        
        This constructor allows initializing the model with custom values for the wave
        travel time (`tau`) and stochastic jam density (`kj`).
        
        Parameter ``p``:
            Pointer to the p_martinez_jin_2020 parameter class containing the model
            parameters.
        """
    def __repr__(self) -> str:
        ...
class model:
    """
    Abstract car-following model class.
    
    This class serves as the base for various car-following models, where vehicles
    adjust their speed based on the behavior of a leading vehicle and certain model-
    specific parameters.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __repr__(self) -> str:
        ...
    def equil_spcg(self, vl: float, vf: float, params: params = None) -> float:
        """
        Compute the equilibrium spacing between vehicles.
        
        This method calculates the equilibrium spacing between the leader and follower
        vehicles based on their velocities and model parameters.
        
        Parameter ``vl``:
            Leader's velocity.
        
        Parameter ``vf``:
            Follower's velocity.
        
        Parameter ``p``:
            Model parameters.
        
        Returns:
            The equilibrium spacing.
        """
    def free_flow_speed(self, params: params = None) -> float:
        """
        Get the free-flow speed of the model.
        
        This method returns the free-flow speed, which is the speed vehicles travel at
        when there are no constraints (such as leading vehicles or road conditions).
        
        Parameter ``p``:
            Model parameters.
        
        Returns:
            The free-flow speed.
        """
    @typing.overload
    def new_point(self, leader: Point, follower: Point, params: params = None) -> Point:
        """
        Compute the next point for a vehicle.
        
        Given the current positions of a leader and follower vehicle, this method
        calculates the next position and speed of the follower.
        
        Parameter ``leader``:
            A point representing the leader's position and speed. Can be null for no
            leader.
        
        Parameter ``follower``:
            A point representing the follower's position and speed.
        
        Parameter ``p``:
            Model parameters.
        
        Returns:
            A point representing the follower's next position and speed.
        """
    @typing.overload
    def new_point(self, leader: GeneralizedTrajectory, follower: Trajectory, params: params = None) -> Point:
        """
        Compute the next point for a vehicle.
        
        Given the current positions of a leader and follower vehicle, this method
        calculates the next position and speed of the follower.
        
        Parameter ``leader``:
            A point representing the leader's position and speed. Can be null for no
            leader.
        
        Parameter ``follower``:
            A point representing the follower's position and speed.
        
        Parameter ``p``:
            Model parameters.
        
        Returns:
            A point representing the follower's next position and speed.
        """
    def validate_parameters(self, params: params = None) -> None:
        """
        Validate the model parameters.
        
        Validates that the model's parameters meet certain constraints. This ensures
        that the model works within its defined boundaries.
        
        Parameter ``p``:
            Parameters for the car-following model. If null, uses the model's internal
            parameters.
        """
    def wave_speed(self, leader: Point, follower: Point, params: params = None) -> float:
        """
        Compute the wave speed of a traffic flow disturbance.
        
        This method computes the wave speed of traffic disturbances based on the
        leader's and follower's positions and velocities.
        
        Parameter ``leader``:
            A point representing the leader's position and velocity.
        
        Parameter ``follower``:
            A point representing the follower's position and velocity.
        
        Parameter ``p``:
            Model parameters.
        
        Returns:
            The computed wave speed (typically 0 unless overridden).
        """
class newell(model):
    """
    Newell's car-following model (2002).
    
    This class implements Newell's car-following model, which is a simplified model
    that describes how vehicles follow one another in traffic. The model assumes
    that each vehicle follows the same trajectory as the vehicle in front but
    delayed by a time gap (τ) and space gap (δ). These parameters are derived from
    the wave speed (w) and jam density (kj), which are the core elements of the
    model.
    
    @note Reference: Newell, G. F. (2002). "A Simplified Car-Following Theory: A
    Lower Order Model." Institute of Transportation Studies, University of
    California, Berkeley.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for Newell's model.
        
        This constructor initializes the model using default values for the wave speed
        (w), jam density (kj), and free-flow speed.
        """
    @typing.overload
    def __init__(self, params: p_newell) -> None:
        """
        Constructor for Newell's model with custom parameters.
        
        This constructor allows initializing the model with custom values for the wave
        speed, jam density, and free-flow speed using the p_newell parameter class.
        
        Parameter ``p``:
            Pointer to the p_newell class containing the parameters for Newell's model.
        """
    def __repr__(self) -> str:
        ...
class newell_constrained_timestep(newell):
    """
    Newell (2002) car-following model with a constrained timestep of 1.
    
    This class is a variant of the Newell car-following model, with the only
    difference being that the timestep is validated and fixed to 1. It inherits all
    properties and functionalities of the original Newell model.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the newell_constrained_timestep model.
        
        This constructor initializes the model using default parameters for Newell’s
        car-following model with the timestep constrained to 1.
        """
    @typing.overload
    def __init__(self, params: p_newell) -> None:
        """
        Constructor with custom parameters for Newell's model.
        
        This constructor allows setting custom values for Newell’s car-following model,
        with the timestep validation constrained to 1.
        
        Parameter ``p``:
            Pointer to the p_newell parameter class containing model parameters.
        """
    def __repr__(self) -> str:
        ...
class newell_random_acceleration(newell):
    """
    Laval et al. (2014) car-following model with random acceleration behavior.
    
    This class implements a variant of Newell’s car-following model that includes
    random acceleration dynamics, as introduced by Laval et al. (2014). The model
    captures variability in driver behavior, incorporating stochastic fluctuations
    in vehicle acceleration.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the random acceleration model.
        
        Initializes the model using default values for both Newell’s and Laval’s model
        parameters, including random acceleration settings.
        """
    @typing.overload
    def __init__(self, params: p_newell_random_acceleration) -> None:
        """
        Constructor with custom parameters for Newell's and Laval's models.
        
        This constructor allows initializing the model with custom values for both
        Newell’s car-following parameters and Laval's random acceleration model
        parameters.
        
        Parameter ``p``:
            Pointer to the p_newell_random_acceleration class containing the parameters.
        """
    def __repr__(self) -> str:
        ...
class no_lch(LCM):
    """
    A lane-changing model that forbids any lane changes.
    
    This class represents a model where no lane-changing maneuvers are allowed. It
    acts as a fallback or placeholder model when lane-changing is not considered in
    a traffic simulation.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        """
        Default constructor for the `no_lch` model.
        
        Initializes the lane-changing model with no parameters and prohibits all lane
        changes.
        """
class p_gipps(params):
    """
    Parameter class for the Gipps car-following model.
    
    This class stores the parameters required for simulating vehicle behavior in the
    Gipps car-following model. The parameters represent key driver behaviors and
    vehicle constraints, such as:
    
    - an: Maximum acceleration that the driver is willing to undertake.
    
    - bn: Maximum deceleration (braking) that the driver considers safe.
    
    - sn: Jam spacing, the minimum distance the driver maintains when the vehicle is
    stopped.
    
    - vn: Free-flow speed, the desired speed when no vehicles are ahead.
    
    - tau: Reaction time, the time it takes for the driver to respond to the vehicle
    ahead.
    
    - bg: Leader's estimated maximum deceleration, used to predict the worst-case
    scenario for sudden braking.
    
    These parameters are essential for reproducing realistic traffic behavior in
    simulations, such as maintaining safe following distances and appropriate speed
    adjustments in response to changing traffic conditions.
    
    Reference: Gipps, P.G. (1981), "A Behavioural Car-Following Model for Computer
    Simulation", Transport Research Part B, Vol. 15, pp. 105-111.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for p_gipps.
        
        Initializes the parameters with default values based on general traffic
        conditions: an = 1.7 m/s² (maximum acceleration), bn = -3.4 m/s² (maximum
        deceleration), sn = 6.5 meters (jam spacing), vn = 120 km/h (free-flow speed),
        tau = 0.8 seconds (reaction time), bg = -3.2 m/s² (leader's estimated maximum
        deceleration).
        """
    @typing.overload
    def __init__(self, an: float, bn: float, sn: float, vn: float, tau: float, bg: float) -> None:
        """
        Constructor with custom parameter values.
        
        This constructor allows initializing the parameters with custom values, allowing
        for specific scenarios to be modeled. These parameters correspond directly to
        driver and vehicle behaviors.
        
        Parameter ``an``:
            Maximum acceleration in m/s².
        
        Parameter ``bn``:
            Maximum deceleration (braking) in m/s².
        
        Parameter ``sn``:
            Jam spacing in meters.
        
        Parameter ``vn``:
            Free-flow speed in m/s.
        
        Parameter ``tau``:
            Reaction time in seconds.
        
        Parameter ``bg``:
            Leader's estimated maximum deceleration in m/s².
        """
    @property
    def an(self) -> float:
        """
        Maximum acceleration in m/s².
        """
    @an.setter
    def an(self, arg0: float) -> None:
        ...
    @property
    def bg(self) -> float:
        """
        Estimated maximum deceleration of the leader in m/s².
        """
    @bg.setter
    def bg(self, arg0: float) -> None:
        ...
    @property
    def bn(self) -> float:
        """
        Maximum deceleration (braking) in m/s².
        """
    @bn.setter
    def bn(self, arg0: float) -> None:
        ...
    @property
    def sn(self) -> float:
        """
        Jam spacing in meters (the minimum safe distance between stopped vehicles).
        """
    @sn.setter
    def sn(self, arg0: float) -> None:
        ...
    @property
    def tau(self) -> float:
        """
        Driver's reaction time in seconds.
        """
    @tau.setter
    def tau(self, arg0: float) -> None:
        ...
    @property
    def vn(self) -> float:
        """
        Free-flow speed in m/s (default value: 120 km/h).
        """
    @vn.setter
    def vn(self, arg0: float) -> None:
        ...
class p_idm(params):
    """
    Parameters for the Intelligent Driver Model (IDM).
    
    This class contains the specific parameters for the Intelligent Driver Model
    (IDM), including maximum desired speed, acceleration and deceleration
    capabilities, and desired time headway. These parameters control the behavior of
    vehicles in the IDM and can be tuned based on empirical data.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor with standard IDM parameters.
        
        Initializes the IDM parameters with default values based on empirical studies.
        
        See also:
            M. Treiber, A. Hennecke, and D. Helbing, "Congested traffic states in
            empirical observations and microscopic simulations," Phys. Rev. E, 62, 1805
            (2000).
        """
    @typing.overload
    def __init__(self, v0: float, T: float, a: float, b: float, s0: float, l: float) -> None:
        """
        Constructor for IDM parameters with custom values.
        
        This constructor allows the user to define custom values for the IDM parameters,
        including maximum speed, time headway, and acceleration properties.
        
        Parameter ``v0``:
            Maximum desired speed (m/s).
        
        Parameter ``T``:
            Desired time headway (s).
        
        Parameter ``a``:
            Maximum acceleration (m/s²).
        
        Parameter ``b``:
            Comfortable deceleration (m/s²).
        
        Parameter ``s0``:
            Minimum gap in congested traffic (m).
        
        Parameter ``l``:
            Vehicle length (m).
        """
    @property
    def T(self) -> float:
        """
        Desired time headway (s).
        """
    @T.setter
    def T(self, arg0: float) -> None:
        ...
    @property
    def a(self) -> float:
        """
        Maximum acceleration (m/s²).
        """
    @a.setter
    def a(self, arg0: float) -> None:
        ...
    @property
    def b(self) -> float:
        """
        Comfortable deceleration (m/s²).
        """
    @b.setter
    def b(self, arg0: float) -> None:
        ...
    @property
    def l(self) -> float:
        """
        Vehicle length (m).
        """
    @l.setter
    def l(self, arg0: float) -> None:
        ...
    @property
    def s0(self) -> float:
        """
        Minimum gap (jam distance) in congested traffic (m).
        """
    @s0.setter
    def s0(self, arg0: float) -> None:
        ...
    @property
    def v0(self) -> float:
        """
        Maximum desired speed (m/s).
        """
    @v0.setter
    def v0(self, arg0: float) -> None:
        ...
class p_laval(params):
    """
    Immutable container holding Laval‑model scalar parameters.
    
    The class fulfils the generic **params** interface used across Autopysta: -
    `required_keys()` – names expected in a JSON / dict config, - `clone()` – deep
    copy through base‑class pointer, - `to_string()` – formatted dump for logs.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Construct with motorway‑style default values.
        """
    @typing.overload
    def __init__(self, u: float, w: float, kj: float, a0: float, vmax: float) -> None:
        """
        Fully specified constructor.
        
        Parameter ``u_free``:
            Free‑flow speed
        
        Parameter ``w_back``:
            Backward wave speed
        
        Parameter ``k_jam``:
            Jam density
        
        Parameter ``a_zero``:
            Max accel at *v*=0
        
        Parameter ``v_max``:
            Mechanical top speed
        """
    @property
    def a0(self) -> float:
        """
        Maximum acceleration at *v*=0 (*a0*).
        """
    @a0.setter
    def a0(self, arg0: float) -> None:
        ...
    @property
    def kj(self) -> float:
        """
        Jam density (*k_j*).
        """
    @kj.setter
    def kj(self, arg0: float) -> None:
        ...
    @property
    def u(self) -> float:
        """
        Free‑flow speed (*u*).
        """
    @u.setter
    def u(self, arg0: float) -> None:
        ...
    @property
    def vmax(self) -> float:
        """
        Mechanical top speed (*v_max*).
        """
    @vmax.setter
    def vmax(self, arg0: float) -> None:
        ...
    @property
    def w(self) -> float:
        """
        Back‑propagating wave speed (*w*).
        """
    @w.setter
    def w(self, arg0: float) -> None:
        ...
class p_lcm_force(params):
    """
    Parameter manager for the force-based 1D lane‑change model.
    
    This class holds exactly two parameters: - _min_accel_gain: Minimum acceleration
    gain (m/s²) required to consider a lane change. - _max_follower_drop: Maximum
    instantaneous velocity drop (m/s) allowed for the would‑be follower.
    
    These thresholds correspond to “Δr” and “dt” as calibrated in Delpiano et al.
    (2020), Table 2, Exp. 3.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the force-based lane-changing parameters.
        
        Initializes to the calibrated defaults: Δr = 2.9 m/s², dt = 20 m/s.
        """
    @typing.overload
    def __init__(self, min_accel_gain: float, max_follower_drop: float) -> None:
        """
        Constructor with custom thresholds.
        
        Parameter ``min_gain``:
            Minimum accel. gain (m/s²).
        
        Parameter ``max_drop``:
            Max follower speed drop (m/s).
        """
    @property
    def max_follower_drop(self) -> float:
        """
        [m/s] maximum follower speed loss allowed
        """
    @max_follower_drop.setter
    def max_follower_drop(self, arg0: float) -> None:
        ...
    @property
    def min_accel_gain(self) -> float:
        """
        [m/s²] minimum accel. gain to trigger a lane change
        """
    @min_accel_gain.setter
    def min_accel_gain(self, arg0: float) -> None:
        ...
class p_lcm_gipps(params):
    """
    Parameter manager for the Gipps (1986) lane-changing model.
    
    This class handles the lane-changing parameters, including the fractions of
    free-flow speed required to initiate overtaking (left lane change) and to revert
    to the original lane (right lane change).
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the Gipps lane-changing model parameters.
        
        Initializes parameters with default values: `_pvl = 0.9` and `_pvh = 0.95`.
        """
    @typing.overload
    def __init__(self, pvlow: float, pvhigh: float) -> None:
        """
        Constructor with custom lane-changing parameters.
        
        Initializes parameters with the given values.
        
        Parameter ``pvlow``:
            Fraction of free-flow speed for overtaking (must be between 0 and 1).
        
        Parameter ``pvhigh``:
            Fraction of free-flow speed for returning to the original lane (must be
            between `pvlow` and 1).
        
        Throws:
            Exception if the input values are not in the range 0 < `pvlow` < `pvhigh` <
            1.
        """
    @property
    def pvh(self) -> float:
        """
        Fraction of free-flow speed for returning (right lane change).
        """
    @pvh.setter
    def pvh(self, arg0: float) -> None:
        ...
    @property
    def pvl(self) -> float:
        """
        Fraction of free-flow speed for overtaking (left lane change).
        """
    @pvl.setter
    def pvl(self, arg0: float) -> None:
        ...
class p_lcm_laval(params):
    """
    Parameter manager for the Laval & Leclercq (2008) lane-changing model.
    
    This class manages the key parameters of the Laval lane-changing model,
    including maneuver duration and relaxation speed deficit.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor using typical values from Laval & Leclercq (2008).
        """
    @typing.overload
    def __init__(self, tau: float, epsilon: float, u: float, w: float, kj: float) -> None:
        """
        Custom parameter constructor.
        
        Parameter ``tau``:
            Mean lane change maneuver duration [s].
        
        Parameter ``eps``:
            Relaxation speed deficit [m/s].
        
        Parameter ``u``:
            Free-flow speed [m/s].
        
        Parameter ``w``:
            Congested wave speed [m/s].
        
        Parameter ``kj``:
            Jam density [veh/m].
        """
    @property
    def epsilon(self) -> float:
        """
        Relaxation speed deficit [m/s], controls the relaxation behavior after the lane
        change.
        """
    @epsilon.setter
    def epsilon(self, arg0: float) -> None:
        ...
    @property
    def tau(self) -> float:
        """
        Mean maneuver duration [s], representing the typical time to complete a lane
        change.
        """
    @tau.setter
    def tau(self, arg0: float) -> None:
        ...
class p_linear(params):
    """
    Parameter class for the linear car-following model.
    
    This class stores the parameters used in the linear car-following model. These
    parameters include:
    
    - Free-flow speed (V): The desired speed when no vehicles are ahead. -
    Coefficients (c1, c2, c3): Constants that control the sensitivity to speed and
    spacing differences. - Jam spacing (sr): The minimum distance maintained between
    vehicles when stopped. - Reaction time (tau): The time it takes for the driver
    to react to changes in the vehicle ahead.
    
    These parameters are essential for simulating vehicle behavior in traffic flow.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for p_linear.
        
        Initializes the parameters with default values based on typical traffic
        conditions: Free-flow speed = 120 km/h, reaction time = 4/6 seconds, and default
        coefficients for speed and spacing.
        """
    @typing.overload
    def __init__(self, V: float, c1: float, c2: float, c3: float, sr: float, tau: float) -> None:
        """
        Constructor with custom parameter values.
        
        This constructor allows setting custom values for the linear model parameters.
        
        Parameter ``V``:
            Free-flow speed in m/s.
        
        Parameter ``c1``:
            Coefficient for speed difference sensitivity.
        
        Parameter ``c2``:
            Coefficient for follower's speed difference sensitivity.
        
        Parameter ``c3``:
            Coefficient for spacing sensitivity.
        
        Parameter ``sr``:
            Jam spacing in meters.
        
        Parameter ``tau``:
            Driver's reaction time in seconds.
        """
    @property
    def V(self) -> float:
        """
        Free-flow speed in m/s (default value: 120 km/h).
        """
    @V.setter
    def V(self, arg0: float) -> None:
        ...
    @property
    def c1(self) -> float:
        """
        Coefficient for speed difference sensitivity.
        """
    @c1.setter
    def c1(self, arg0: float) -> None:
        ...
    @property
    def c2(self) -> float:
        """
        Coefficient for follower's speed difference sensitivity.
        """
    @c2.setter
    def c2(self, arg0: float) -> None:
        ...
    @property
    def c3(self) -> float:
        """
        Coefficient for spacing sensitivity.
        """
    @c3.setter
    def c3(self, arg0: float) -> None:
        ...
    @property
    def sr(self) -> float:
        """
        Jam spacing (minimum distance between vehicles when stopped).
        """
    @sr.setter
    def sr(self, arg0: float) -> None:
        ...
    @property
    def tau(self) -> float:
        """
        Driver's reaction time in seconds.
        """
    @tau.setter
    def tau(self, arg0: float) -> None:
        ...
class p_martinez_jin_2020(p_newell):
    """
    Parameter class for Martinez and Jin (2020) stochastic car-following model.
    
    This class defines the parameters for the Martinez and Jin (2020) model, an
    extension of Newell's car-following theory. The model accounts for heterogeneous
    driver behavior by introducing a wave travel time parameter (`tau`) and
    stochastic jam density.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the p_martinez_jin_2020 parameter class.
        
        Initializes the model with default values for wave travel time (`tau`) and
        inherited parameters from the Newell model.
        """
    @typing.overload
    def __init__(self, u: float, tau: float) -> None:
        """
        Constructor with custom parameter values.
        
        Allows setting custom values for the free-flow speed (`u`) and wave travel time
        (`tau`).
        
        Parameter ``u``:
            Free-flow speed in meters per second.
        
        Parameter ``tau``:
            Wave travel time in seconds.
        """
    @property
    def tau(self) -> float:
        """
        Wave travel time (τ), controlling the delay in vehicle reactions to changes in
        traffic.
        """
    @tau.setter
    def tau(self, arg0: float) -> None:
        ...
class p_newell(params):
    """
    Parameter class for Newell's car-following model.
    
    The p_newell class manages the specific parameters required for Newell's car-
    following model. These parameters control the behavior of vehicles in free-flow
    and congested traffic conditions.
    
    Key Parameters: - Free-flow speed (`u`): The speed at which vehicles travel
    under free-flow conditions (i.e., no congestion). This is typically set in
    meters per second. - Wave speed (`w`): The speed at which congestion waves
    propagate backward through the traffic. This helps simulate how quickly
    disturbances in the flow of traffic spread. - Jam density (`kj`): The density of
    vehicles in a jammed traffic condition, which helps define the minimum spacing
    between vehicles.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for p_newell.
        
        Initializes the parameters with default values for free-flow speed, wave speed,
        and jam density. These defaults represent typical traffic conditions.
        
        Default Values: - Free-flow speed: 90 km/h - Wave speed: 18 km/h - Jam density:
        0.15 vehicles per meter
        """
    @typing.overload
    def __init__(self, u: float, w: float, kj: float) -> None:
        """
        Constructor with custom parameter values.
        
        This constructor allows setting custom values for free-flow speed (`u`), wave
        speed (`w`), and jam density (`kj`). These values can be used to simulate
        specific traffic scenarios.
        
        Parameter ``u``:
            Free-flow speed in meters per second.
        
        Parameter ``w``:
            Wave speed in meters per second.
        
        Parameter ``kj``:
            Jam density in vehicles per meter.
        """
    @property
    def kj(self) -> float:
        """
        Jam density in vehicles per meter (default: 0.15 vehicles/meter).
        """
    @kj.setter
    def kj(self, arg0: float) -> None:
        ...
    @property
    def u(self) -> float:
        """
        Free-flow speed in meters per second (default: 90 km/h).
        """
    @u.setter
    def u(self, arg0: float) -> None:
        ...
    @property
    def w(self) -> float:
        """
        Wave speed in meters per second (default: 18 km/h).
        """
    @w.setter
    def w(self, arg0: float) -> None:
        ...
class p_newell_random_acceleration(p_newell):
    """
    Parameter class for the random acceleration model based on Laval et al. (2014).
    
    This class manages the specific parameters required for Laval's random
    acceleration extension to Newell's car-following model. These parameters control
    the stochastic behavior of vehicles in traffic simulations.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor for the random acceleration parameters.
        
        Initializes the parameters with default values based on typical traffic
        conditions.
        """
    @typing.overload
    def __init__(self, u: float, w: float, kj: float, sigma_tilde: float, beta: float) -> None:
        """
        Constructor with custom parameter values.
        
        This constructor allows setting custom values for the standard deviation
        (`sigma_tilde`), inverse relaxation time (`beta`), as well as inherited
        parameters from p_newell.
        
        Parameter ``u``:
            Free-flow speed in meters per second.
        
        Parameter ``w``:
            Wave speed in meters per second.
        
        Parameter ``kj``:
            Jam density in vehicles per meter.
        
        Parameter ``sigma_tilde``:
            Standard deviation of the random acceleration term.
        
        Parameter ``beta``:
            Inverse relaxation time.
        """
    @property
    def beta(self) -> float:
        """
        Inverse relaxation time, affecting the temporal responsiveness of vehicles.
        """
    @beta.setter
    def beta(self, arg0: float) -> None:
        ...
    @property
    def sigma_tilde(self) -> float:
        """
        Standard deviation of the random acceleration term.
        """
    @sigma_tilde.setter
    def sigma_tilde(self, arg0: float) -> None:
        ...
class params:
    """
    Base class for car-following model parameters.
    
    This class is a base class that stores common or general parameters used by
    various car-following models. Specific models, such as `newell`, will have their
    own parameter sets that inherit from this class.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class params_cust(params):
    """
    Custom parameters class for storing key-value pairs.
    
    This class inherits from the `params` class and stores custom parameters in a
    dictionary-like structure. The `params_cust` class allows for flexible key-value
    pair storage of parameters.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __getitem__(self, key: str) -> float:
        """
        Get parameter value like a dictionary: p['V']
        """
    def __init__(self) -> None:
        """
        Initializes the dictionary for custom parameters.
        """
    def __repr__(self) -> str:
        ...
    def __setitem__(self, key: str, value: float) -> None:
        """
        Set parameter value like a dictionary: p['V'] = 33.0
        """
    def add(self, name: str, value: float) -> None:
        """
        Adds a new parameter to the dictionary.
        
        Adds a new parameter to the dictionary.
        
        Parameter ``new_name``:
            Key or name of the parameter.
        
        Parameter ``new_value``:
            Value associated with the parameter.
        """
    def get(self, name: str) -> float:
        """
        Retrieves the value of a parameter by its key.
        
        Parameter ``name``:
            Key or name of the parameter to retrieve.
        
        Returns:
            The value associated with the given key.
        """
def version() -> str:
    """
    Get the software version information.
    
    This function returns a string that contains the current version of the
    software, along with the build date, time, and the system platform (Linux or
    Windows). It also includes the version of Python being used in the environment.
    
    Returns:
        A string containing version, build date, system platform, and Python
        version.
    """
