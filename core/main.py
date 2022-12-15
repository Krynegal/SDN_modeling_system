#!/usr/bin/python
import os
import sys
import threading
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
from utils import host_addr_map, get_receivers, get_senders, fwd_activate
from scripters import generate_custom, generate_all_to_all, read_custom_traffic
from runners import run_all, run_custom, run_stats_processing
from onos.main import get_intents_to_send, post_intents, get_src_dst_map, get_links, \
    get_dijkstra_graph, get_hosts, hosts_func, read_all_to_all, get_host_switch_map, get_switch_start_pairs, \
    get_src_dst_switch_map_reachability_matrix
from onos.stats import read_weights_matrix

net = Mininet()

c0 = net.addController('c0', controller=RemoteController, ip='172.17.0.2', port=6653)

core_path = '/home/andre/PycharmProjects/onos_short_path/core/'
scripts_path = core_path + 'scripts/'
itg_path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin'
topo_file = 'topologies/fat_tree.txt'
topo_path = core_path + topo_file


class Node():
    def __init__(self, data, indexloc=None):
        self.data = data
        self.index = indexloc


class Graph():
    @classmethod
    def create_from_nodes(self, nodes):
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

        matrix = [[0] * len(nodes) for _ in range(len(nodes))]
        with open(topo_path, "r") as f:
            for line in f.readlines():
                src, dst = map(int, line.strip().split(", "))
                matrix[src - 1][dst - 1] = 1
                matrix[dst - 1][src - 1] = 1

        graph.adj_mat = matrix
        hosts = []
        switches = []
        print('len(graph.nodes): ', len(graph.nodes))
        for i in range(len(graph.nodes)):
            switches.append(self.addSwitch('s' + graph.nodes[i].data, protocols="OpenFlow13"))
            #hosts.append(self.addHost('h' + str(i + 1), ip='192.168.0.' + str(i + 1)))
            if i < 8:
                h_num = i*2
                hosts.append(self.addHost('h' + str(h_num + 1), ip='192.168.0.' + str(h_num + 1)))
                hosts.append(self.addHost('h' + str(h_num + 2), ip='192.168.0.' + str(h_num + 2)))
                self.addLink(switches[i], hosts[h_num], bw=1000)
                self.addLink(switches[i], hosts[h_num+1], bw=1000)

        # add links between switches
        for row in range(len(graph.adj_mat)):
            for col in range(row, len(graph.adj_mat[row])):
                if graph.adj_mat[row][col] != 0:
                    self.addLink(switches[row], switches[col], bw=1000)


topo = MyTopo()
net = Mininet(topo=topo, controller=RemoteController, build=False, link=TCLink)
net.addController(c0)
net.build()
net.start()
time.sleep(5)
net.pingAll()

fwd_activate(False)

host_addr_map = host_addr_map(topo)
hosts = []
for h_key in host_addr_map.keys():
    hosts.append(net.get(f'h{h_key}'))
# devices_num = len(hosts)
switches_num = 20
# print(hosts)


def parse_p_args(input):
    rate, size, time, protocol = input[1], input[2], input[3], input[4]
    return rate, size, time, protocol


def delete_old_files():
    os.system(f'cd {itg_path} && ./deleteLogs.sh')
    os.system(f'cd {itg_path} && ./deleteDat.sh')
    os.system(f'cd {itg_path} && ./deleteTxt.sh')


while True:
    print('input "m" to run mininet console')
    print('input "c" to run custom')
    print('input "g <rate> <size> <time (ms)> <protocol>" to generate scripts')
    input_line = input().split()
    if len(input_line) == 1 and input_line[0] == 'm':
        CLI(net)
    elif input_line[0] == 'c':
        delete_old_files()
        os.system(f'rm -rf {core_path}actions/*')
        read_data = get_yaml_content()

        links = get_links()
        graph = get_dijkstra_graph(links)
        hosts_list = get_hosts()
        #hsm = get_host_switch_map(hosts_list)
        # h = hosts_func(hosts_list)
        # на основании traffic - [['1', '2'], ..., ['2', '10']] - строится матрица достижимости
        reachability_matrix = [[0] * switches_num for x in range(switches_num)]
        # src_dst_map строится на основании матрицы достижимости, так как она по сути ей и является только в другой форме

        threads = []
        all_receivers = []
        mutex = threading.Lock()
        for action in read_data['scenario']:
            start_time = action['script']['time']
            time.sleep(start_time)
            custom_t_file_path = core_path + action['script']['name']
            duration = action['script']['duration']
            id = action['script']['id']

            traffic = read_custom_traffic(custom_t_file_path)

            # === принимаем решение о создании интента ===
            # проверяем содержится ли пара src-dst из traffic в матрице достижимости
            # если да, то НЕ кладем эту пару в src_dst_map
            # если нет, то кладем эту пару в src_dst_map и обновляем матрицу достижимости
            switch_start_pairs = get_switch_start_pairs(traffic)
            print(switch_start_pairs)
            src_dst_switch_map = get_src_dst_switch_map_reachability_matrix(reachability_matrix, traffic)
            if len(src_dst_switch_map) != 0:
                if id != 1:
                    # обновляем матрицу графа дейкстры
                    graph.adj_mat = read_weights_matrix()
                intents = get_intents_to_send(graph, hosts_list, links, src_dst_switch_map, switch_start_pairs)
                post_intents(intents)
            else:
                print("src_dst_map is empty. There are no new intents")

            receivers = get_receivers(traffic)
            senders = get_senders(traffic)
            generate_custom(id, host_addr_map, traffic, duration)

            if id == 1:
                time.sleep(20)
                stat_thread = Thread(name="stats thread", target=run_stats_processing, args=(links, switches_num,))
                stat_thread.start()
                threads.append(stat_thread)

            scripts_path = core_path + f'actions/action{id}/'
            name = str(id)
            thread = Thread(name=name, target=run_custom, args=(scripts_path, hosts, senders, receivers, all_receivers, duration,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            print(f"thread {thread} is STOPPED")
            thread.join()

        print("here")
        for i in range(1, len(hosts) + 1):
            hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')

    elif input_line[0] == 'g':
        delete_old_files()
        if len(input_line) == 1:
            generate_all_to_all(host_addr_map)
            run_all(hosts)
        elif len(input_line) == 5:
            rate, size, time, protocol = parse_p_args(input_line)
            generate_all_to_all(host_addr_map, rate, size, time, protocol)
            run_all(hosts)
        else:
            print('some args were skipped')
            continue
    elif input_line[0] == 'k':
        for i in range(1, len(hosts) + 1):
            hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')
    elif input_line[0] == 'q':
        break

net.stop()
