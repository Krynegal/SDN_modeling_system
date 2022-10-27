#!/usr/bin/python
import os
import sys
import time
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import RemoteController

conf_path = os.getcwd()
sys.path.append(conf_path)
from utils import host_addr_map, get_receivers, get_senders
from scripters import generate_custom, generate_all_to_all, read_custom_traffic
from runners import run_all, run_custom

net = Mininet()

c0 = net.addController('c0', controller=RemoteController, ip='172.17.0.2', port=6653)

core_path = '/home/andre/PycharmProjects/onos_short_path/core/'
scripts_path = core_path + 'scripts/'
itg_path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin'
topo_file = 'topologies/edges10.txt'
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
            hosts.append(self.addHost('h' + str(i + 1), ip='192.168.0.' + str(i + 1)))
            self.addLink(switches[i], hosts[i])

        # add links between switches
        for row in range(len(graph.adj_mat)):
            for col in range(row, len(graph.adj_mat[row])):
                if graph.adj_mat[row][col] != 0:
                    self.addLink(switches[row], switches[col])


topo = MyTopo()
net = Mininet(topo=topo, controller=RemoteController, build=False)
net.addController(c0)
net.build()
net.start()
time.sleep(5)
net.pingAll()

host_addr_map = host_addr_map(topo)
hosts = []
for h_key in host_addr_map.keys():
    hosts.append(net.get(f'h{h_key}'))
print(hosts)


def parse_p_args(input):
    rate, size, protocol = input[1], input[2], input[3]
    return rate, size, protocol


def delete_old_files():
    os.system(f'cd {itg_path} && ./deleteLogs.sh')
    os.system(f'cd {itg_path} && ./deleteDat.sh')


while True:
    print('input "m" to run mininet console')
    print('input "c" to run custom')
    print('input "g <rate> <size> <protocol>" to generate scripts')
    input_line = input().split()
    if len(input_line) == 1 and input_line[0] == 'm':
        CLI(net)
    elif input_line[0] == 'c':
        delete_old_files()
        traffic = read_custom_traffic()
        receivers = get_receivers(traffic)
        senders = get_senders(traffic)
        generate_custom(host_addr_map, traffic)
        run_custom(hosts, senders, receivers)
    elif input_line[0] == 'g':
        delete_old_files()
        if len(input_line) == 1:
            generate_all_to_all(host_addr_map)
            run_all(hosts)
        elif len(input_line) == 4:
            rate, size, protocol = parse_p_args(input_line)
            generate_all_to_all(host_addr_map, rate, size, protocol)
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
