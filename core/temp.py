import random
import time
from copy import copy, deepcopy

import numpy as np

if __name__ == '__main__':
    # switch_controller_map = {}
    # with open("/home/andre/PycharmProjects/onos_short_path/core/switch_controller.txt", "r") as f:
    #     for line in f.readlines():
    #         splited_line = line.strip().split(", ")
    #         switch, controller = map(int, splited_line)
    #         switch_controller_map[switch] = controller
    weight_funcs = {
        1: 10,
        2: 20,
    }

    switch_controller_map = {
        1: 1,
        2: 1,
        3: 1,
        4: 2,
        5: 2,
        6: 2
    }

    matrix = np.array(
        [[-1, 1, 2, -1, 3, -1],
         [1, -1, -1, 4, -1, -1],
         [2, -1, -1, -1, -1, -1],
         [-1, 4, -1, -1, 5, -1],
         [3, -1, -1, 5, -1, 6],
         [-1, -1, -1, -1, 6, -1]])

    for i in range(6):
        for j in range(i):
            if matrix[i][j] == -1:
                continue
            elif switch_controller_map[i+1] == switch_controller_map[j+1]:
                v = weight_funcs[switch_controller_map[i+1]]
            else:
                v = weight_funcs[random.randint(1, len(weight_funcs))]
            matrix[i][j] = v
            matrix[j][i] = v
            print(f'i: {i+1} j: {j+1} v: {v}')
    print(matrix)

    # weight_matrix = np.where(matrix == -1, 0, 16)

    # with open("custom_traffics/custom_traffic_200.txt", "w") as f:
    #     f.write("UDP; ")
    #     recv = [_ for _ in range(1, 200+1)]
    #     random.shuffle(recv)
    #     for s in range(1, 200+1):
    #         f.write(f'{s},{recv[s-1]}; ')

    # with open("topologies/fat_tree_100.txt", "w") as f:
    #     x = 40  # кол-во свитчей на двух нижний уровнях в 3-х уровневой топологии
    #     for i in range(1, x+1):
    #         f.write(f'{i}, {i+x}\n')
    #         if i % 2 != 0:
    #             f.write(f'{i}, {i + x + 1}\n')
    #         else:
    #             f.write(f'{i}, {i + x - 1}\n')
    #     lvl3 = [_ for _ in range(2*x+1, (2*x+1)+int(x/2))]
    #     print(lvl3)
    #     for i in range(x+1, 2*x+1):
    #         if i % 2 != 0:
    #             for j in lvl3[:int(len(lvl3)/2)]:
    #                 f.write(f'{i}, {j}\n')
    #         else:
    #             for j in lvl3[int(len(lvl3)/2):]:
    #                 f.write(f'{i}, {j}\n')
    #
    # with open("fat_tree_hosts_100.txt", "w") as f:
    #     x = 40  # кол-во свитчей на двух нижний уровнях в 3-х уровневой топологии
    #     for i in range(1, x+1):
    #         f.write(f'{i}, {i+x}\n')
    #         if i % 2 != 0:
    #             f.write(f'{i}, {i + x + 1}\n')
    #         else:
    #             f.write(f'{i}, {i + x - 1}\n')
    #     lvl3 = [_ for _ in range(2*x+1, (2*x+1)+int(x/2))]
    #     print(lvl3)
    #     for i in range(x+1, 2*x+1):
    #         if i % 2 != 0:
    #             for j in lvl3[:int(len(lvl3)/2)]:
    #                 f.write(f'{i}, {j}\n')
    #         else:
    #             for j in lvl3[int(len(lvl3)/2):]:
    #                 f.write(f'{i}, {j}\n')
