import random

if __name__ == '__main__':
    with open("/home/andre/PycharmProjects/onos_short_path/core/topologies/fat_tree_hosts_100.txt", "r") as f:
        lines = f.readlines()
        lastSwitchNum = ""
        for line in lines:
            h, s = line.strip().split(', ')
            if s != lastSwitchNum:
                port_num = 0
                lastSwitchNum = s
            port_num += 1
            print(h, s, port_num)

    # with open("custom_traffic_test.txt", "w") as f:
    #     f.write("UDP; ")
    #     recv = [_ for _ in range(1, 192+1)]
    #     random.shuffle(recv)
    #     for s in range(1, 192+1):
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
