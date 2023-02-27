import os
import random
import time
from copy import copy, deepcopy
import subprocess
import numpy as np

if __name__ == '__main__':
    # ip = subprocess.check_output("docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' atomix-1", universal_newlines=True)
    # ip = subprocess.check_output("docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' atomix-1", shell=True)
    ip = os.popen(f"docker inspect -f '{{{{range.NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' atomix-1").read()
    print(ip)
    #print(ip.strip())

    # switch_controller_map = {}
    # with open("/home/andre/PycharmProjects/onos_short_path/core/switch_controller.txt", "r") as f:
    #     for line in f.readlines():
    #         splited_line = line.strip().split(", ")
    #         switch, controller = map(int, splited_line)
    #         switch_controller_map[switch] = controller


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
