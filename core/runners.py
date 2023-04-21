import datetime
import time
from threading import Thread
import numpy as np

from core.weight_functions import weight_funcs
from onos.ford_fulkerson import Graph as ff_graph
from onos.stats import get_spm, get_stats
from configs.configs import core_path, itg_path, onos_path


def run_custom(scripts_path: str, hosts: [], senders: [], receivers: [], all_receivers: [], duration):
    print(f'receivers: {receivers}')
    print(f'ALL receivers: {all_receivers}')
    print(f'senders: {senders}')
    print('---start of processing---')
    print('processing...')

    receivers_start = datetime.datetime.now()
    print(f'\n [!!!] start receivers creation at {receivers_start.strftime("%H:%M:%S:%f")}')
    for i in range(len(receivers)):
        if receivers[i] not in all_receivers:
            all_receivers.append(receivers[i])
            hosts[int(receivers[i]) - 1].cmd(f'cd {itg_path} && ./ITGRecv -l recv{receivers[i]}.log &')
    receivers_end = datetime.datetime.now()
    print(f'[!!!] all receivers have been created at {receivers_end.strftime("%H:%M:%S:%f")}')
    receivers_duration = receivers_end - receivers_start
    hours, remainder = divmod(receivers_duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f'receivers creation took {minutes}:{seconds}\n')
    time.sleep(1)

    senders_start = datetime.datetime.now()
    print(f'\n [!!!] start senders creation at {senders_start.strftime("%H:%M:%S:%f")}')
    for i in senders:
        hosts[int(i) - 1].cmd(f'cd {itg_path} && ./ITGSend {scripts_path}script{i} -l send{i}.log &')
        print(f'sender {i} started at {datetime.datetime.now().strftime("%H:%M:%S:%f")}')
    senders_end = datetime.datetime.now()
    print(f'[!!!] all senders have been created at {senders_end.strftime("%H:%M:%S:%f")}')
    senders_duration = senders_end - senders_start
    hours, remainder = divmod(senders_duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f'senders creation took {minutes}:{seconds}\n')
    time.sleep(int(duration))


def write_matrix(f, matrix):
    for line in matrix:
        np.savetxt(f, line, fmt='%7.2f,', newline=' ')
        f.write("\n")
    f.write("\n")


def run_stats_processing(links, num_devices: int, duration, switch_controller_file):
    #matrix = np.full((num_devices, num_devices), -1)
    matrix = np.full((num_devices, num_devices), 0)
    src_ports_map = get_spm(links)
    threads = []

    # определяем, к какому контроллеру принадлежит линк
    switch_controller_map = {}
    with open(f"{core_path}/{switch_controller_file}", "r") as f:
        for line in f.readlines():
            splited_line = line.strip().split(", ")
            switch, controller = map(int, splited_line)
            switch_controller_map[switch] = controller

    for t in range(2, duration + 1, 2):
        time.sleep(2)
        thread = Thread(name=f"stats thread {t}", target=temp,
                        args=(matrix, src_ports_map, t, switch_controller_map,))
        thread.start()
        threads.append(thread)
        print(f'start stats thread {t} at {datetime.datetime.now().strftime("%H:%M:%S")}')
    for thread in threads:
        thread.join()


def weight_func(df, edge):
    return df[edge][0] * (df[edge][1] / 1000) if edge in df else 0


def temp(matrix, src_ports_map, t, switch_controller_map):
    matrix = get_stats(matrix, src_ports_map)
    n = len(matrix)
    weight_matrix = np.full((n, n), 0.0)
    print(f'\nmatrix:\n{matrix}\n')

    # вот тут врубаем Форда-Фалкерсона на матрице остаточной пропускной способности
    df = {}  # {i, j} : [frequency, max_flow_sum]
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i == j:
                continue
            g = ff_graph(matrix)
            max_flow, min_cut = g.ff(i, j)
            if max_flow != 0:
                for edge in min_cut:
                    if frozenset(edge) not in df:
                        df[frozenset(edge)] = [1, max_flow]
                    else:
                        df[frozenset(edge)] = [df[frozenset(edge)][0] + 1, df[frozenset(edge)][1] + max_flow]
                #print(f'max flow from {i} to {j} = {max_flow}; min cut: {min_cut}')
            else:
                print(f'there is no path from {i} to {j}')
    print(f'\ndf: {df}\nlen(df):{len(df)}\n')

    for i in range(n):
        for j in range(i):
            if matrix[i][j] == -1:
                continue
            if switch_controller_map[i + 1] == switch_controller_map[j + 1]:
                w_func = weight_funcs[switch_controller_map[i + 1]]
            else:
                w_func = weight_funcs[2]
            #weight_matrix[i][j] = w_func(matrix[i][j])
            # ford fulkerson
            weight_matrix[i][j] = round(w_func(df, frozenset({i, j})), 2)
            weight_matrix[j][i] = weight_matrix[i][j]

    with open(f"{onos_path}/weights.txt", "w") as f:
        write_matrix(f, weight_matrix)
    with open(f"{onos_path}/weights_all.txt", "a+") as f:
        f.write(f"=======================================  {t} seconds  ========================================\n")
        write_matrix(f, weight_matrix)
