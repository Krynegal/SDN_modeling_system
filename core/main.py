#!/usr/bin/python
import os
import sys
import time
from threading import Thread

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import RemoteController

conf_path = os.getcwd()
sys.path.append("/home/andre/PycharmProjects/onos_short_path/onos")
sys.path.append("/usr/lib64/python310.zip")
sys.path.append("/usr/lib64/python3.10")
sys.path.append("/usr/lib64/python3.10/lib-dynload")
sys.path.append("/home/andre/.local/lib/python3.10/site-packages")
sys.path.append("/usr/local/lib64/python3.10/site-packages")
sys.path.append("/usr/lib64/python3.10/site-packages")
sys.path.append("/usr/lib/python3.10/site-packages")
sys.path.append("..")
sys.path.append(conf_path)
print(sys.path)

from core.read_scenario import get_yaml_content
from utils import get_host_addr_map, get_receivers, get_senders
from scripters import generate_custom, read_custom_traffic
from runners import run_custom, run_stats_processing
from onos.main import get_intents_to_send, get_switch_start_pairs, get_src_dst_switch_map_reachability_matrix, \
    remove_duplicates, get_hosts_info, to_onos_device, to_hex
from onos.dijkstra import get_dijkstra_graph
from onos.stats import read_weights_matrix
from onos.api import post_intents, get_links, get_hosts, fwd_activate


class Node:
    def __init__(self, data, indexloc=None):
        self.data = data
        self.index = indexloc


class Graph:
    @classmethod
    def create_from_nodes(cls, nodes):
        return Graph(len(nodes), len(nodes), nodes)

    def __init__(self, row, col, nodes=None):
        self.adj_mat = [[0] * col for _ in range(row)]
        self.nodes = nodes
        for i in range(len(self.nodes)):
            self.nodes[i].index = i


class MyTopo(Topo):
    def build(self):
        fwd_activate(True)
        nodes = []
        with open(topo_path, "r") as f:
            for line in f.readlines():
                nodes.extend(line.strip().split(", "))

        nodes = list(set(nodes))
        nodes.sort(key=int)
        print(nodes)
        for i in range(len(nodes)):
            nodes[i] = Node(nodes[i])

        graph = Graph.create_from_nodes(nodes)

        # матрица соединений свитчей
        matrix = [[0] * len(nodes) for _ in range(len(nodes))]
        with open(topo_path, "r") as f:
            for line in f.readlines():
                src, dst = map(int, line.strip().split(", "))
                matrix[src - 1][dst - 1] = 1
                matrix[dst - 1][src - 1] = 1

        # мапа хост : свитч
        host_switch_conn = {}
        with open(topo_path_hosts, "r") as f:
            for line in f.readlines():
                host, switch = map(int, line.strip().split(", "))
                host_switch_conn[host] = switch

        graph.adj_mat = matrix
        switches = []
        print('len(graph.nodes): ', len(graph.nodes))
        # создаем все свитчи
        for i in range(len(graph.nodes)):
            switches.append(self.addSwitch('s' + graph.nodes[i].data, protocols="OpenFlow13"))
        # создаем все хосты и коннектим их с их свитчами
        for host_num in host_switch_conn:
            host = self.addHost(f'h{host_num}', ip=f'192.168.{host_num // 255}.{host_num % 255 + (host_num // 255)}')
            self.addLink(host, switches[host_switch_conn[host_num] - 1])

        # add links between switches
        for row in range(len(graph.adj_mat)):
            for col in range(row, len(graph.adj_mat[row])):
                if graph.adj_mat[row][col] != 0:
                    self.addLink(switches[row], switches[col])


def delete_old_files():
    os.system(f'cd {itg_path} && ./deleteLogs.sh')
    os.system(f'cd {itg_path} && ./deleteDat.sh')
    os.system(f'cd {itg_path} && ./deleteTxt.sh')


core_path = '/home/andre/PycharmProjects/onos_short_path/core/'
scripts_path = core_path + 'scripts/'
itg_path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin'
topo_file = 'topologies/fat_tree.txt'
switch_hosts_conn_file = 'topologies/fat_tree_hosts_test.txt'
topo_path = core_path + topo_file
topo_path_hosts = core_path + switch_hosts_conn_file


def weight_func(x):
    return 1000 / (1000 - x)


def find_max_flow_duration(read_data):
    max_dur = 0
    for s in read_data["scenario"]:
        max_dur = max(s["script"]["duration"], max_dur)
    return max_dur


def gen_host_switch_pair():
    h_num = 1
    with open(f"{core_path}/topologies/fat_tree_hosts_test.txt", "w") as f:
        for s in range(1, 8 + 1):
            for h in range(1, 24 + 1):
                f.write(f'{h_num}, {s}\n')
                h_num += 1


def ping(host, addresses):
    for addr in addresses:
        host.cmd(f'ping {addr} -c 1 -q')


def pingall(hosts, addresses):
    threads = []
    for i in range(len(hosts)):
        host = hosts[i]
        thread = Thread(target=ping, args=(host, addresses))
        threads.append(thread)
        thread.start()

    for thread in threads:
        print(f"thread {thread} is STOPPED")
        thread.join()


def get_hosts_info_2(net):
    hosts_info = {}
    with open(f"/home/andre/PycharmProjects/onos_short_path/core/topologies/fat_tree_hosts_test.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            h, s = line.strip().split(', ')
            net_host = net.get(f'h{h}')
            res = net_host.cmd("ifconfig | awk 'FNR==2||FNR==4{print $2}'")
            ip, mac = [x.strip() for x in res.split("\n")][:2]
            port = str(int(h) % 25 + (int(h) // 25))
            switch = int(s)
            onos_switch = to_onos_device(to_hex(switch))
            hosts_info[h] = {
                "mac": mac,  # string
                "port": port,  # string
                "switch": switch,  # int, example: 1..192
                "onos_switch": onos_switch,  # string of:00000000000000a
            }
    return hosts_info


def main():
    gen_host_switch_pair()

    net = Mininet()
    c0 = net.addController('c0', controller=RemoteController, ip='172.17.0.2', port=6653)
    topo = MyTopo()
    net = Mininet(topo=topo, controller=RemoteController, build=False, link=TCLink)
    net.addController(c0)
    net.build()
    net.start()
    time.sleep(5)

    print(topo.g.node)
    topo_nodes = topo.g.node
    host_addr_map = get_host_addr_map(topo_nodes)
    hosts = []
    for h_key in host_addr_map.keys():
        hosts.append(net.get(f'h{h_key}'))
    switches_num = 0
    for node in topo_nodes:
        if 'isSwitch' in topo_nodes[node] and topo_nodes[node]["isSwitch"]:
            switches_num += 1
    print(f'switchesNum: {switches_num}\n')

    print(host_addr_map.values())

    # net.pingAll()
    # hosts_list = get_hosts()
    # hosts_info = get_hosts_info(hosts_list)
    # print(f"hosts_info: {hosts_info}")

    print(f"get_hosts_info_2(net): {get_hosts_info_2(net)}")
    # pingall(hosts, host_addr_map.values())
    # fwd_activate(False)

    while True:
        print('input "m" to run mininet console')
        print('input "c" to run custom')
        input_line = input().split()
        if len(input_line) == 1 and input_line[0] == 'm':
            CLI(net)
        elif input_line[0] == 'c':
            # чистим файлы, оставшиеся после прошлых запусков
            delete_old_files()
            os.system(f'rm -rf {core_path}actions/*')

            # строим граф, который будем использовать для поиска путей минимальной стоимости
            links = get_links()
            graph = get_dijkstra_graph(links)

            # hosts_list = get_hosts()
            # hosts_info = get_hosts_info(hosts_list)

            hosts_info = get_hosts_info_2(net)

            # матрица достижимости для свитчей
            reachability_matrix = [[0] * switches_num for _ in range(switches_num)]

            threads = []
            all_receivers = []
            read_data = get_yaml_content()
            max_flow_duration = find_max_flow_duration(read_data)
            for action in read_data['scenario']:
                # получаем информацию об очередном потоке
                id = action['script']['id']
                start_time = action['script']['time']
                duration = action['script']['duration']
                print(f"{action['script']['id']} in cycle! sleep {start_time} seconds")
                time.sleep(start_time)

                # получаем трафик, который будет передаваться в потоке
                custom_t_file_path = core_path + action['script']['name']
                traffic = read_custom_traffic(custom_t_file_path)

                host_pairs_only = remove_duplicates(traffic[0][1])

                # TODO: упаковать в функцию
                # мапа хост : свитч
                host_switch_conn = {}
                with open(topo_path_hosts, "r") as f:
                    for line in f.readlines():
                        host, switch = map(int, line.strip().split(", "))
                        host_switch_conn[host] = switch
                # определяем свитчи, которые будут использоваться в качестве стартовых нод для пар [<src, dst>,
                # ... ] из трафика
                switch_start_pairs = get_switch_start_pairs(host_pairs_only, host_switch_conn)
                print(f'switch_start_pairs {switch_start_pairs}')
                src_dst_switch_map = get_src_dst_switch_map_reachability_matrix(reachability_matrix, traffic,
                                                                                host_switch_conn)
                if len(src_dst_switch_map) != 0:
                    if id != 1:
                        # обновляем матрицу весов графа
                        graph.adj_mat = read_weights_matrix()
                    intents = get_intents_to_send(graph, hosts_info, links, src_dst_switch_map, switch_start_pairs)
                    post_intents(intents)
                else:
                    print("src_dst_map is empty. There are no new intents")

                receivers = get_receivers(traffic)
                senders = get_senders(traffic)
                generate_custom(id, host_addr_map, traffic, duration)

                if id == 1:
                    time.sleep(40)
                    stat_thread = Thread(name="stats thread", target=run_stats_processing,
                                         args=(links, switches_num, max_flow_duration, weight_func,))
                    stat_thread.start()
                    threads.append(stat_thread)

                scripts_path = core_path + f'actions/action{id}/'
                name = str(id)
                thread = Thread(name=name, target=run_custom,
                                args=(scripts_path, hosts, senders, receivers, all_receivers, duration,))
                thread.start()
                print(f'thread: {thread.name} is started')
                threads.append(thread)

            for thread in threads:
                print(f"thread {thread} is STOPPED")
                thread.join()

            print("all threads are stopped")
            for i in range(1, len(hosts) + 1):
                hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')
        elif input_line[0] == 'k':
            for i in range(1, len(hosts) + 1):
                hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')
        elif input_line[0] == 'q':
            break
    net.stop()


main()
