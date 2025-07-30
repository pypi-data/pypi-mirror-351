from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from math import ceil
import numpy as np

class Point:
    def __init__(self, x_real, x_adjusted, y, lane, velocity_y, time, leader_id=None):
        self.x_real = x_real
        self.x_adjusted = x_adjusted
        self.y = y
        self.lane = lane
        self.velocity_y = velocity_y
        self.time = time
        self.leader_id = leader_id

def add_to_dict(dictionary, key1, key2, point):
    if key1 not in dictionary:
        dictionary[key1] = {}
    dictionary[key1][key2] = point
    

class Trajectories:
    def __init__(self, time_steps, trajectory_data, dt=0.1, lane_width=3.6576,
                 num_lanes=-1, max_y=-1, lane_markings=[]):
        """
        Parameters:
            time_steps (dict): Dictionary of time step data.
            trajectory_data (dict): Dictionary of trajectory data keyed by vehicle id.
            dt (float): Time delta between steps.
            lane_width (float): Width of a lane.
            num_lanes (int): Number of lanes. If -1, it is determined from the data.
            max_y (float): Maximum y-value; if -1, determined from the data.
            lane_markings (list): List of lane marking positions.
        """
        self._time_steps = time_steps
        self._trajectory_data = trajectory_data
        self._dt = dt
        self._lane_width = lane_width
        self._max_y = max_y
        self._num_lanes = num_lanes
        self._lane_markings = lane_markings
        self._limits = []

        # Uncomment below to use default lane markings if none are provided.
        # if not lane_markings:
        #     self._lane_markings = [0, self._num_lanes * self._lane_width]

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'bs')

        if max_y == -1:
            self._max_y = max(max(point.y for point in traj.values())
                              for traj in self._trajectory_data.values())
            self._min_y = min(min(point.y for point in traj.values())
                              for traj in self._trajectory_data.values())
        if num_lanes == -1:
            if not lane_markings:
                self._num_lanes = max(max(point.lane for point in traj.values())
                                      for traj in self._trajectory_data.values())
            else:
                self._num_lanes = len(lane_markings) - 1
        print('Number of lanes =', self._num_lanes)

    def _draw_lane_lines(self, figure_obj):
        plt.figure(figure_obj.number)
        if not self._lane_markings:
            for i in range(1, self._num_lanes):
                plt.plot([self._lane_width * i, self._lane_width * i],
                         [0, self._max_y], 'k--')
        else:
            for marking in self._lane_markings:
                plt.plot([marking, marking], [0, self._max_y], 'k--')

    def animate_all(self):
        self.animate_time_steps(self._time_steps.keys())

    def init_animation(self):
        self.line.set_data([], [])
        if not self._limits:
            if not self._lane_markings:
                self.ax.set_xlim([0, self._num_lanes * self._lane_width])
            else:
                self.ax.set_xlim([self._lane_markings[0], self._lane_markings[-1]])
            self.ax.set_ylim([self._min_y, self._max_y])
        else:
            self.ax.set_xlim([self._limits[0], self._limits[1]])
            self.ax.set_ylim([self._limits[2], self._limits[3]])
        return self.line,

    def update_animation(self, time_step):
        if time_step not in self._time_steps:
            return self.line,

        x_coords = [self._time_steps[time_step][vehicle_id].x_adjusted 
                    for vehicle_id in self._time_steps[time_step]]
        y_coords = [self._time_steps[time_step][vehicle_id].y 
                    for vehicle_id in self._time_steps[time_step]]

        self.line.set_data(x_coords, y_coords)
        self._draw_lane_lines(self.fig)

        # Hide previous annotations
        for annotation in self.ax.texts:
            annotation.set_visible(False)

        # Annotate each vehicle with its id
        for vehicle_id, point in self._time_steps[time_step].items():
            self.ax.annotate(vehicle_id, xy=(point.x_adjusted, point.y),
                             xytext=(0, 0), textcoords='offset points')

        return self.line,



    def animate_time_steps(self, time_steps):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'bs')
        animation = FuncAnimation(self.fig, self.update_animation, frames=time_steps,
                                  interval=100, init_func=self.init_animation)
        plt.show()

    def draw_trajectories(self, vehicle_ids):
        fig = plt.figure()
        for vehicle_id in vehicle_ids:
            self.draw_trajectory(vehicle_id, fig, show_lane_lines=False)
        self._draw_lane_lines(fig)

    def draw_trajectory(self, vehicle_id, figure_obj=None, show_lane_lines=True):
        if vehicle_id not in self._trajectory_data:
            return
        if figure_obj is None:
            figure_obj = plt.figure()
        else:
            plt.figure(figure_obj.number)
        sorted_time_steps = sorted(self._trajectory_data[vehicle_id].keys())
        x_coords = [self._trajectory_data[vehicle_id][t].x_adjusted for t in sorted_time_steps]
        y_coords = [self._trajectory_data[vehicle_id][t].y for t in sorted_time_steps]
        plt.plot(x_coords, y_coords, '-')
        if show_lane_lines:
            self._draw_lane_lines(figure_obj)

    def compute_states_xts(self):
        results = []
        eddie_area = self._max_y * ((len(self._lane_markings) / 2) - 1) * self._dt
        for ts_data in self._time_steps.values():
            total_time = [0, 0]
            total_distance = [0, 0]
            for point in ts_data.values():
                index = 0 if point.velocity_y > 0 else 1
                total_time[index] += self._dt
                total_distance[index] += abs(point.velocity_y) * self._dt
            # Append q, k, v values
            results.append([total_distance[1] / eddie_area,
                            total_time[1] / eddie_area,
                            total_distance[1] / total_time[1]])
        return results

    

    def compute_states(self, y_min, y_max, n_steps, lane):
        results = []
        num_intervals = ceil((len(self._time_steps) + 1) / n_steps)
        sum_delta_y = [0] * num_intervals
        sum_delta_t = [0] * num_intervals
        for trajectory in self._trajectory_data.values():
            for time_step, point in trajectory.items():
                if lane == point.lane:
                    dt_adjusted = self._dt
                    y_next = point.y + dt_adjusted * point.velocity_y
                    interval_index = int(time_step / n_steps)
                    # If the vehicle is in the region for part or all of the time step
                    if y_min < y_next and point.y < y_max:
                        # Adjust dt if the point is just before entering the region
                        if point.y < y_min:
                            dt_adjusted = (y_next - y_min) / point.velocity_y
                        # Adjust dt if the point is just before leaving the region
                        if y_max < y_next:
                            dt_adjusted = (y_max - point.y) / point.velocity_y
                        sum_delta_t[interval_index] += dt_adjusted
                        sum_delta_y[interval_index] += dt_adjusted * point.velocity_y
        eddie_area = (y_max - y_min) * self._dt * n_steps
        for delta_t, delta_y in zip(sum_delta_t, sum_delta_y):
            if delta_t == 0:
                results.append([abs(delta_y) / eddie_area, 0, 0])
            else:
                results.append([abs(delta_y) / eddie_area, delta_t / eddie_area, abs(delta_y) / delta_t])
        return results

    def get_time_steps(self):
        return self._time_steps

    def get_trajectory_data(self):
        return self._trajectory_data

    def get_leader_and_follower_by_db(self, vehicle_id):
        first_time_step = min(self._trajectory_data[vehicle_id].keys())
        first_point = self._trajectory_data[vehicle_id][first_time_step]
        leader_id = first_point.leader_id
        leader_positions = []
        leader_velocities = []
        follower_positions = []
        follower_velocities = []
        time_step = first_time_step
        while leader_id != 0:
            ts_data = self._time_steps[time_step]
            leader_id = ts_data[vehicle_id].leader_id
            follower_positions.append(ts_data[vehicle_id].y)
            follower_velocities.append(ts_data[vehicle_id].velocity_y)
            leader_positions.append(ts_data[leader_id].y)
            leader_velocities.append(ts_data[leader_id].velocity_y)
            time_step += 1
        return leader_positions, leader_velocities, follower_positions, follower_velocities

    def get_leader_and_follower(self, vehicle_id=None):
        if vehicle_id is None:
            vehicle_id = next(iter(self._trajectory_data))
        first_time_step = min(self._trajectory_data[vehicle_id].keys())
        first_point = self._trajectory_data[vehicle_id][first_time_step]
        lane = first_point.lane
        y_initial = first_point.y
        leader_y = float('inf')
        leader_id = -1
        for vid, point in self._time_steps[first_time_step].items():
            if point.lane == lane and point.y > y_initial and point.y < leader_y:
                leader_y = point.y
                leader_id = vid
        vehicle_time_steps = list(self._trajectory_data[vehicle_id].keys())
        if leader_id != -1:
            leader_time_steps = list(self._trajectory_data[leader_id].keys())
        t0 = max(min(vehicle_time_steps), min(leader_time_steps))
        tf = min(max(vehicle_time_steps), max(leader_time_steps))
        leader_positions = []
        leader_velocities = []
        follower_positions = []
        follower_velocities = []
        for ts in range(t0, tf + 1):
            ts_data = self._time_steps[ts]
            follower_positions.append(ts_data[vehicle_id].y)
            follower_velocities.append(ts_data[vehicle_id].velocity_y)
            leader_positions.append(ts_data[leader_id].y)
            leader_velocities.append(ts_data[leader_id].velocity_y)
        return leader_positions, leader_velocities, follower_positions, follower_velocities


    def _set_limits(self, x_min, x_max, y_min, y_max):
        self._limits = [x_min, x_max, y_min, y_max]

    def set_limits(self, x_min, x_max, y_min, y_max):
        self._set_limits(x_min, x_max, y_min, y_max)
        for ts_data in self._time_steps.values():
            for point_id in list(ts_data.keys()):
                point = ts_data[point_id]
                if point.x_adjusted < x_min or point.x_adjusted > x_max or point.y < y_min or point.y > y_max:
                    del ts_data[point_id]

    def rotate(self, angle_degrees):
        x_all = [point.x_adjusted for ts_data in self._time_steps.values() for point in ts_data.values()]
        y_all = [point.y for ts_data in self._time_steps.values() for point in ts_data.values()]

        vectors_matrix = np.array([x_all, y_all])
        angle_radians = np.radians(angle_degrees)
        rotation_matrix = np.array([[np.cos(angle_radians), -np.sin(angle_radians)],
                                    [np.sin(angle_radians),  np.cos(angle_radians)]])
        rotated_vectors = np.dot(rotation_matrix, vectors_matrix)

        min_x = min(rotated_vectors[0])
        max_x = max(rotated_vectors[0])
        min_y = min(rotated_vectors[1])
        max_y = max(rotated_vectors[1])

        self._set_limits(min_x, max_x, min_y, max_y)

        index = 0
        for ts_data in self._time_steps.values():
            for point in ts_data.values():
                point.x_adjusted = rotated_vectors[0][index]
                point.y = rotated_vectors[1][index]
                index += 1

# READ FUNCTIONS OUTSIDE Trajectories CLASS
def read_custom(filename,colid=-1,colx=-1,coly=-1,coltstep=-1,colvy=-1,colvehwidth=-1,collid=-1,median=-1,sep=" ",dt=0.1,mulseps=True,lanewidth=3.6576,ft2m=True,nlanes=-1,maxy=-1,skipfirst=False,lanemarkings=[],**kwargs):
    dts = {}
    did = {}
    a=open(filename)
    if skipfirst: a.readline()
    for f in a:
        m=f.strip().split(sep)
        if mulseps:
            n=m.count('')
            for i in range(n):
                m.remove('')
        vid=int(m[colid])
        lid=None#int(m[collid])
        x=float(m[colx])
        if(colvehwidth!=-1):
            x+=float(m[colvehwidth])/2
        y=float(m[coly])
        vy=float(m[colvy])
        tstep=int(m[coltstep])
        #convierte a metros y coords relativas
        if ft2m:
            x=x*.3048
            y=y*.3048
        if len(lanemarkings)==0:
            p=1+int((x+0.000001)/lanewidth)
            xr=x%lanewidth-lanewidth/2
        else:
            p=0
            while lanemarkings[p]<x: p+=1
            xr=x-(lanemarkings[p]+lanemarkings[p-1])/2
        if p<median:
            pt=Point(-xr,-x,-y,p,-vy,tstep,lid)
        else:
            pt=Point(xr,x,y,p,vy,tstep,lid)
        add_to_dict(dts,tstep,vid,pt)
        add_to_dict(did,vid,tstep,pt)
    t = Trajectories(dts,did,dt,lanewidth,nlanes,maxy,lanemarkings)
    return t

def read_highD(filename, lanemarkings=[]):
    _id=1
    _t=0 #en dt=1/25s
    _x=3
    _y=2
    _ln=24
    _vy=6
    _ax=9
    _vehw=5
    _ts=.04
    lmkrs = lanemarkings

    t = read_custom(filename, _id, _x, _y, _t, _vy,
                      colvehwidth=_vehw,
                    #   colax=_ax,
                      dt=_ts,
                      sep=",",
                      skipfirst=True,
                      lanemarkings=lmkrs,
                      ft2m=False)
    return t

def read_data_from_sky(filename, lanemarkings=[]):
    sep=";"
    skipfirst=True
    ft2m=False
    mulseps=True
    lanewidth=3.6576
    colvehwidth=-1
    median=-1
    maxy=-1
    nlanes=-1
    colid=0
    coltstep=5 #en dt=1/25s
    colx=0
    coly=1
    colvy=2
    dt=(1/30)
    dts = {}
    did = {}
    a=open(filename)
    if skipfirst: a.readline()
    for f in a:
        m=f.strip().split(sep)
        if mulseps:
            n=m.count('')
            for i in range(n):
                m.remove('')
        vid=int(m[colid])
        lid=None#int(m[collid])
        for i in range(8, len(m), 6):
            x=float(m[i+colx]) #8, 14, 20, 26
            if(colvehwidth!=-1):
                x+=float(m[colvehwidth])/2
            y=float(m[i+coly])
            vy=float(m[i+colvy])
            tstep=round(float(m[i+coltstep])*30)
            #convierte a metros y coords relativas
            if ft2m:
                x=x*.3048
                y=y*.3048
            if len(lanemarkings)==0:
                p=1+int((x+0.000001)/lanewidth)
                xr=x%lanewidth-lanewidth/2
            else:
                p=0
                while lanemarkings[p]<x: p+=1
                xr=x-(lanemarkings[p]+lanemarkings[p-1])/2
            if p<median:
                pt=Point(-xr,-x,-y,p,-vy,tstep,lid)
            else:
                pt=Point(xr,x,y,p,vy,tstep,lid)
            add_to_dict(dts,tstep,vid,pt)
            add_to_dict(did,vid,tstep,pt)
    t = Trajectories(dts,did,dt,lanewidth,nlanes,maxy,lanemarkings)
    return t

def read_ngsim(filename):
    iid=0
    ifr=1
    it=3
    ix=4
    iy=5
    t = read_custom(filename, iid, ix, iy, ifr, 11)
    return t

def read_results(file):
    vid = 0
    dts = {}
    did = {}
    lanewidth=3.6576
    lanemarkings = []
    dt = 0.1
    nlanes = -1
    maxy = -1
    ft2m=False
    median = -1
    for traj in file: #file deberia ser un results.all_lanes()
        vid = vid + 1
        for point in range(len(traj)):
            x = lanewidth*traj[point].LANE() - (lanewidth/2) # w*l - w/2 = (2wl-w) / 2
            y = traj[point].X()
            lid=None#int(m[collid])
            vy=traj[point].V()
            tstep=round(traj[point].T() * 10)
            #convierte a metros y coords relativas
            if ft2m:
                x=x*.3048
                y=y*.3048
            if len(lanemarkings)==0:
                p=1+int((x+0.000001)/lanewidth)
                xr=x%lanewidth-lanewidth/2
            else:
                p=0
                while lanemarkings[p]<x: p+=1
                xr=x-(lanemarkings[p]+lanemarkings[p-1])/2
            if p<median:
                pt=Point(-xr,-x,-y,p,-vy,tstep,lid)
            else:
                pt=Point(xr,x,y,p,vy,tstep,lid)
            add_to_dict(dts,tstep,vid,pt)
            add_to_dict(did,vid,tstep,pt)
    t = Trajectories(dts,did,dt,lanewidth,nlanes,maxy,lanemarkings)
    return t
