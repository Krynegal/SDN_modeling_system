import time
from onos.stats import get_spm, get_stats

core_path = '/home/andre/PycharmProjects/onos_short_path/core/'
scripts_path = core_path + 'scripts/'
itg_path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin'


def run_custom(scripts_path: str, hosts: [], senders: [], receivers: [], all_receivers: [], duration):
    print(f'receivers: {receivers}')
    print(f'ALL receivers: {all_receivers}')
    print(f'senders: {senders}')
    print('---start of processing---')
    print('processing...')

    # for i in receivers:
    #     if i not in all_receivers:
    #         hosts[int(i) - 1].cmd('kill -9 $(pidof ITGRecv)')

    for i in range(len(receivers)):
        if receivers[i] not in all_receivers:
            all_receivers.append(receivers[i])
            hosts[int(receivers[i]) - 1].cmd(f'cd {itg_path} && ./ITGRecv -l recv{receivers[i]}.log &')
        if i == len(receivers) - 1:
            time.sleep(1)

    for i in senders:
        hosts[int(i) - 1].cmd(f'cd {itg_path} && ./ITGSend {scripts_path}script{i} -l send{i}.log &')
    time.sleep(duration)


def run_stats_processing(links, num_devices: int):
    src_ports_map = get_spm(links)
    for t in range(1, 31):
        time.sleep(2)
        matrix = get_stats(src_ports_map, num_devices)
        with open("/home/andre/PycharmProjects/onos_short_path/onos/weights.txt", "w") as f:
            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    f.write('%7.2f, ' % (calc_new_weight(matrix[i][j])))
                f.write('\n')
        with open("/home/andre/PycharmProjects/onos_short_path/onos/weights_all.txt", "a+") as f:
            f.write(f"================================  {int(t) * 2} seconds  ==================================\n")
            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    f.write('%7.2f, ' % (calc_new_weight(matrix[i][j])))
                f.write('\n')
            f.write('\n\n')


def calc_new_weight(matrix_el):
    if matrix_el == -1:
        return 0
    return 1000 / (1000 - matrix_el)
