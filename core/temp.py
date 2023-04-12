import os
import random
import datetime
import time
from copy import copy, deepcopy
import subprocess
import numpy as np

def f():
    random.seed(datetime.datetime.now())
    rand_num = random.randint(0, 1000) / 10
    print(rand_num)
    if rand_num < 1.6:
        return 1515, 2000
    elif rand_num < 4.9:
        return 256, 511
    elif rand_num < 8.5:
        return 512, 1023
    elif rand_num < 13.9:
        return 128, 255
    elif rand_num < 31.7:
        return 1514, 1514
    elif rand_num < 65.1:
        return 64, 127
    elif rand_num < 100:
        return 1024, 1513

if __name__ == '__main__':
    x, y = f()
    print(x, y)
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
    #     for i in range(1, x + 1):
    #         f.write(f'{i}, {i + x}\n')
    #         if i % 2 != 0:
    #             f.write(f'{i}, {i + x + 1}\n')
    #         else:
    #             f.write(f'{i}, {i + x - 1}\n')
    #     lvl3 = [_ for _ in range(2 * x + 1, (2 * x + 1) + int(x / 2))]
    #     print(lvl3)
    #     for i in range(x + 1, 2 * x + 1):
    #         if i % 2 != 0:
    #             for j in lvl3[:int(len(lvl3) / 2)]:
    #                 f.write(f'{i}, {j}\n')
    #         else:
    #             for j in lvl3[int(len(lvl3) / 2):]:
    #                 f.write(f'{i}, {j}\n')

    #create custom traffic четное нечетному и наоборот
    # with open("custom_traffics/custom_traffic_exp.txt", "w") as f:
    #     f.write("UDP; ")
    #     for i in range(16):
    #         for j in range(16):
    #             if i % 2 == 0 and j % 2 != 0 or i % 2 != 0 and j % 2 == 0:
    #                 f.write(f'{i+1},{j+1}; ')

    # create custom traffic all-to-all
    # with open("custom_traffics/custom_traffic_80_ata.txt", "w") as f:
    #     f.write("UDP; ")
    #     for i in range(80):
    #         for j in range(80):
    #             if i == j:
    #                 continue
    #             f.write(f'{i+1},{j+1}; ')

    #create fat_tree_hosts
    # with open("topologies/fat_tree_hosts_80.txt", "w") as f:
    #     j = 1
    #     c = 0
    #     for i in range(80):
    #         if c == 2:
    #             j += 1
    #             c = 0
    #         f.write(f'{i+1}, {j}\n')
    #         c += 1

    # create switch_controller for 2 controllers
    # with open("switch_controller_100_2.txt", "w") as f:
    #     for i in range(1, 100+1):
    #         if i <= 20 or (i >= 41 and i <= 60) or (i >= 81 and i <= 90):
    #             f.write(f"{i}, 1\n")
    #         else:
    #             f.write(f"{i}, 2\n")

    # create switch_controller for 1 controllers
    with open("switch_controller_100_1.txt", "w") as f:
        for i in range(1, 100+1):
            f.write(f"{i}, 1\n")