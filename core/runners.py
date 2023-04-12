import datetime
import time
from threading import Thread
import numpy as np

from core.weight_functions import weight_funcs
from onos.stats import get_spm, get_stats
from configs.configs import core_path, itg_path, onos_path


def run_custom(scripts_path: str, hosts: [], senders: [], receivers: [], all_receivers: [], duration):
    print(f'receivers: {receivers}')
    print(f'ALL receivers: {all_receivers}')
    print(f'senders: {senders}')
    print('---start of processing---')
    print('processing...')

    for i in range(len(receivers)):
        if receivers[i] not in all_receivers:
            all_receivers.append(receivers[i])
            hosts[int(receivers[i]) - 1].cmd(f'cd {itg_path} && ./ITGRecv -l recv{receivers[i]}.log &')
        if i == len(receivers) - 1:
            time.sleep(1)

    for i in senders:
        hosts[int(i) - 1].cmd(f'cd {itg_path} && ./ITGSend {scripts_path}script{i} -l send{i}.log &')
    time.sleep(int(duration))


def write_matrix(f, matrix):
    for line in matrix:
        np.savetxt(f, line, fmt='%7.2f,', newline=' ')
        f.write("\n")
    f.write("\n")


def run_stats_processing(links, num_devices: int, duration, switch_controller_file):
    matrix = np.full((num_devices, num_devices), -1)
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


def temp(matrix, src_ports_map, t, switch_controller_map):
    matrix = get_stats(matrix, src_ports_map)
    n = len(matrix)
    weight_matrix = np.full((n, n), 0.0)

    for i in range(n):
        for j in range(i):
            if matrix[i][j] == -1:
                continue
            elif switch_controller_map[i + 1] == switch_controller_map[j + 1]:
                w_func = weight_funcs[switch_controller_map[i + 1]]
            else:
                w_func = weight_funcs[2]
            weight_matrix[i][j] = w_func(matrix[i][j])
            weight_matrix[j][i] = weight_matrix[i][j]

    with open(f"{onos_path}/weights.txt", "w") as f:
        write_matrix(f, weight_matrix)
    with open(f"{onos_path}/weights_all.txt", "a+") as f:
        f.write(f"=======================================  {t} seconds  ========================================\n")
        write_matrix(f, weight_matrix)
