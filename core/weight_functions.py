import math


def w_func1(bandwidth, x):
    return (x / bandwidth) + 1


def w_func2(bandwidth, x):
    return (x / bandwidth)**2 + 1

# jusn residual bandwidth
def ff_func(df, bandwidth, edge):
    return (df[edge][0] * (df[edge][1] / bandwidth)) / 1000 if edge in df else 0


def residual_bandwidth(bandwidth, x):
    return (bandwidth-x) / bandwidth * 100 + 1 if x != 0 else 0


def ff_func1(df, bandwidth, edge):     
    return (df[edge][0] * (df[edge][1] / (bandwidth * min_cut_length))) / 1000 if edge in df else 0


def f1(df, bandwidth, edge, x, min_cut_length):
    return (bandwidth-x) * df[edge][0] * (df[edge][1] / (bandwidth * min_cut_length)) / 10000 if edge in df else 0


def risidual_bw_use_percent(df, bandwidth, edge, x):
    return (bandwidth-x) * df[edge][0] if edge in df else 0


# sqrt( throughput**2 + percentage of usage in min cuts**2 )
def squared(df, bandwidth, edge, x, num_mincut):
    t = 0
    if edge in df:
        t = df[edge][0]
        print(f'df[edge][0] {df[edge][0]}')
    return math.sqrt(((bandwidth - x) * 100 / bandwidth) ** 2 + (t * 100 / num_mincut) ** 2) + 1 if x != 0 else 0


def squared_3_params(df, bandwidth, edge, x, num_mincut):
    t = 0
    mf = 0
    if edge in df:
        t = df[edge][0]
        mf = df[edge][1]
        print(f'df[edge][0] {df[edge][0]}')
    return math.sqrt(((bandwidth - x) * 100 / bandwidth)** 2 + (t * 100 / num_mincut)** 2 + (mf / 1000)** 2) + 1 if x != 0 else 0


def dijkstra(x):
    return 1 if x != 0 else 0


def ff(df, bandwidth, edge):
    t = 0
    return (df[edge][0] * df[edge][1]) / 10_000 if edge in df else 0


weight_funcs = {
    1: dijkstra,
    2: dijkstra,
}
