import time

from onos.main import get_intents_to_send, post_intents, get_src_dst_map, read_custom_traffic, get_links, \
    get_dijkstra_graph, get_hosts, hosts_func, read_all_to_all
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

    for i in receivers:
        if i not in all_receivers:
            hosts[int(i) - 1].cmd('kill -9 $(pidof ITGRecv)')

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
        with open("/home/andre/PycharmProjects/onos_short_path/onos/weights_all.txt", "a") as f:
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


def run_all(hosts: []):
    links = get_links()

    graph = get_dijkstra_graph(links)
    hosts_list = get_hosts()
    h = hosts_func(hosts_list)
    src_dst_map = read_all_to_all(h)
    intents = get_intents_to_send(graph, h, links, src_dst_map)
    post_intents(intents)

    time.sleep(20)
    hosts_num = len(hosts)
    print('---start of processing---')
    print('processing...')
    for i in range(1, hosts_num + 1):
        hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')
    for i in range(1, hosts_num + 1):
        hosts[i - 1].cmd(f'cd {itg_path} && ./ITGRecv -l recv_all_{i}.log &')
    time.sleep(3)

    for i in range(1, hosts_num + 1):
        hosts[i - 1].cmd(f'cd {itg_path} && ./ITGSend {scripts_path}script{i} -l send_all_{i}.log &')

    src_ports_map = get_spm(links)
    for t in range(1, 31):
        matrix = get_stats(src_ports_map, len(h))
        with open("/home/andre/PycharmProjects/onos_short_path/onos/weights.txt", "w") as f:
            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    f.write('%7.2f, ' % (calc_new_weight(matrix[i][j])))
                f.write('\n')
        with open("/home/andre/PycharmProjects/onos_short_path/onos/weights_all.txt", "a") as f:
            f.write(f"================================  {int(t) * 2} seconds  ==================================\n")
            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    f.write('%7.2f, ' % (calc_new_weight(matrix[i][j])))
                f.write('\n')
            f.write('\n\n')
        time.sleep(2)

    # time.sleep(60)
    for i in range(1, len(hosts) + 1):
        hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')
    print('---end of processing---')
