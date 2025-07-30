from pathlib import Path
import typer
import autonomous_proto
from typing import Annotated
from rosbags.highlevel import AnyReader
import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt

def foi_update(y_prev, u, K, tc, T):
    if tc <= 1e-9:
        return y_prev
    return y_prev + (K * u - y_prev) * min(T / tc, 1.0)

def simulate(params, u, y0, T):
    K, tc, delay_steps = params
    y_predicted = np.zeros(len(u))
    y_predicted[0] = y0
    u_foi = np.zeros(len(u))
    for i in range(len(u)):
        index = i - delay_steps
        if index < 0:
            u_foi[i] = u[0]
        elif index >= len(u):
            u_foi[i] = u[-1]
        else:
            u_foi[i] = u[index]
    for i in range(len(u) - 1):
        y_predicted[i + 1] = foi_update(y_predicted[i], u_foi[i], K, tc, T)
    return y_predicted

def objective(params, delay_steps, u, y, T):
    K, tc = params
    return y - simulate((K, tc, delay_steps), u, y[0], T)

def identify(c, v, T, K_max, K_min, tc_max, tc_min, delay_steps_max):
    min_sse = float('inf')
    best_params = None
    initial_params = np.array([1.0, (tc_max + tc_min) * 0.5], dtype=float)
    bounds = ([K_min, tc_min], [K_max, tc_max])
    for delay_steps in range(delay_steps_max + 1):
        result = least_squares(
            objective,
            x0=initial_params,
            args=(delay_steps, c, v, T),
            bounds=bounds,
        )
        if result.success:
            K_opt, tc_opt = result.x
            residuals = result.fun
            sse = np.sum(residuals ** 2)
            print(f"Delay steps: {delay_steps}, K={K_opt:.4f}, tc={tc_opt:.4f}, SSE={sse:.3e}")
            if sse < min_sse:
                min_sse = sse
                best_params = {
                    'K': K_opt,
                    'tc': tc_opt,
                    'delay_steps': delay_steps,
                    'T': T,
                    'sse': sse
                }
        else:
            print(f"Optimization failed for delay steps {delay_steps}: {result.message}")
    return best_params

def extract(data: list[tuple[autonomous_proto.Control, autonomous_proto.VehicleState]]):
    c = []
    v = []
    t = []
    t0 = data[0][1].header.info.timestamp * 1e-9
    for control, vehicle_state in data:
        c.append(control.k[0])
        v.append(vehicle_state.k[0])
        t.append(vehicle_state.header.info.timestamp * 1e-9 - t0)
    c = np.array(c)
    v = np.array(v)
    t = np.array(t)
    return c, v, t

def read_bag(bag: Path):
    matched: list[tuple[autonomous_proto.Control, autonomous_proto.VehicleState]] = []
    if not bag.exists():
        print('Bag file not found')
        return matched
    print('File: ', bag.absolute())
    control_protos: list[autonomous_proto.Control] = []
    vehicle_state_protos: list[autonomous_proto.VehicleState] = []
    with AnyReader([bag.expanduser()]) as reader:
        for connection, t, rawdata in reader.messages():
            if connection.topic == "/control" or connection.topic == "control":
                msg = reader.deserialize(rawdata, connection.msgtype)
                if hasattr(msg, 'data'):
                    control_protos.append(autonomous_proto.Control.FromString(bytes(msg.data)))
            if connection.topic == "/vehicle_state" or connection.topic == "vehicle_state":
                msg = reader.deserialize(rawdata, connection.msgtype)
                if hasattr(msg, 'data'):
                    vehicle_state_protos.append(autonomous_proto.VehicleState.FromString(bytes(msg.data)))
    print('control protos size      : ', len(control_protos))
    print('vehicle state protos size: ', len(vehicle_state_protos))
    vs_iter = iter(vehicle_state_protos)
    cur_vs = next(vs_iter, None)
    for control_proto in control_protos:
        for source in control_proto.header.sources:
            if source.topic_name != autonomous_proto.MessageInfoTopicNameValue.vehicle_state:
                continue
            while cur_vs and cur_vs.header.info.count < source.count:
                cur_vs = next(vs_iter, None)
            if cur_vs and cur_vs.header.info.count == source.count:
                matched.append((control_proto, cur_vs))
    print('matched size             : ', len(matched))
    return matched

def display_cvt(c, v, t):
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, c, label='c', color='blue', marker='.')
    plt.plot(t, v, label='v', color='orange', marker='.')
    plt.xlabel('Time (s)')
    plt.grid()
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(t, c - v, label='Difference (c - v)', color='green')
    plt.xlabel('Time (s)')
    plt.ylabel('Difference (c - v)')
    plt.grid()
    plt.legend()

    plt.tight_layout()
    plt.show()


app = typer.Typer(invoke_without_command=True, help='identify foi parameters')
@app.callback()
def main_callback(
    bag: Annotated[Path, typer.Argument(help='Path to the bag file',)],
    interval: Annotated[float, typer.Option(help='Interval per step in seconds')] = None,
    k_max: Annotated[float, typer.Option(help='Maximum K value')] = 1.03,
    k_min: Annotated[float, typer.Option(help='Minimum K value')] = 0.97,
    tc_max: Annotated[float, typer.Option(help='Maximum time constant (tc)')] = 2.0,
    tc_min: Annotated[float, typer.Option(help='Minimum time constant (tc)')] = 0.01,
    delay_steps_max: Annotated[int, typer.Option(help='Maximum delay steps')] = 30,
    display: Annotated[bool, typer.Option(help='Display graphs')] = False,
):
    matched = read_bag(bag)
    if not matched:
        print('No valid data found in the bag file')
        return
    c, v, t = extract(matched)
    if display:
        display_cvt(c, v, t)
    if interval is None:
        interval = t[1] - t[0]
    best_params = identify(c, v, interval, k_max, k_min, tc_max, tc_min, delay_steps_max)
    print(best_params)


if __name__ == "__main__":
    app()
