#!/usr/bin/python

import time

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
import os
from mininet.node import OVSSwitch, RemoteController

#import traffic_types
#from traffic_types import read_traffic_types, get_host_map, make_skripts, get_receivers, get_senders

net = Mininet()

c0 = net.addController('c0', controller=RemoteController, ip='172.17.0.2', port=6653)

onos_project_path = '/home/andre/PycharmProjects/onos_short_path/'
path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin'
customPath = '/home/andre/mininet/custom/'
topo_file = 'sixSwitches.txt'
topo_path = onos_project_path + topo_file


def read_traffic_types():
    res = []
    with open("traffic_types.txt", "r") as f:
        for line in f.readlines():
            splited_line = line.strip("\n").split(";")
            protocol = splited_line[0]
            pairs = [x.strip().split(",") for x in splited_line[1:]]
            res.append([protocol, pairs])
    print(res)
    return res

def get_host_map(nodes):
    m = {}
    for node in nodes:
        if 'ip' in nodes[node]:
            m[node[1:]] = nodes[node]['ip']
    print(m)
    return m

def get_receivers(traffic):
    receivers = []
    for t in traffic:
        for n in t[1]:
            receivers.append(n[1])
    return list(set(receivers))

def get_senders(traffic):
    senders = []
    for t in traffic:
        for n in t[1]:
            senders.append(n[0])
    return list(set(senders))

def make_skripts(traffic, h_map):
    os.system(f'cd {onos_project_path} && rm script*')
    for t in traffic:
        for h in t[1]:
            with open(f"script{h[0]}", "a") as f:
                f.writelines(f"-a {h_map[h[1]]} -C 1000 -c 500 -T {t[0]}\n")
            os.chmod(rf"script{h[0]}", 0o777)


##############################################################################################33

def get_ip_addrs(topo):
    g_nodes = topo.g.node
    addrs = []
    hosts_num = 0
    for node_v in g_nodes.values():
        if 'ip' in node_v:
            addrs.append(node_v["ip"])
            hosts_num += 1
    return addrs, hosts_num


def generate_scripts(addrs, rate=1000, pkt_size=512, protocol='UDP'):
    for i in range(len(addrs)):
        with open(f"script{i + 1}", "w") as f:
            for j in range(len(addrs)):
                if i == j:
                    continue
                f.writelines(f"-a {addrs[j]} -C {rate} -c {pkt_size} -T {protocol}\n")
        os.chmod(rf"script{i}.txt", 0o777)

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
        print(nodes)

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
time.sleep(3)

addrs, hosts_num = get_ip_addrs(topo)
list_of_hosts = []
for i in range(1, hosts_num + 1):
    list_of_hosts.append(net.get(f'h{i}'))
print(list_of_hosts)


def parse_p_args(input):
    rate, size, protocol = input[1], input[2], input[3]
    return rate, size, protocol


def run_custom(senders, receivers):
    print('---start of processing---')
    print('processing...')
    print('receivers', receivers)
    for i in receivers:
        list_of_hosts[int(i) - 1].cmd('kill -9 $(pidof ITGRecv)')
    for i in receivers:
        list_of_hosts[int(i) - 1].cmd('cd ' + path + f' && ./ITGRecv -l recv{i}.log &')
    time.sleep(3)

    print('senders', senders)
    for i in senders:
        list_of_hosts[int(i) - 1].cmd('cd ' + path + f' && ./ITGSend {onos_project_path}script{i} -l send_{i}_to_all.log &')
    time.sleep(5)
    print('---end of processing---')

def run():
    print('---start of processing---')
    print('processing...')
    for i in range(1, hosts_num + 1):
        list_of_hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')
    for i in range(1, hosts_num + 1):
        list_of_hosts[i - 1].cmd('cd ' + path + f' && ./ITGRecv -l recv{i}.log &')
    time.sleep(3)

    for i in range(1, hosts_num + 1):
        list_of_hosts[i - 1].cmd('cd ' + path + f' && ./ITGSend {customPath}script{i} -l send_{i}_to_all.log &')
    time.sleep(5)
    print('---end of processing---')


while True:
    print('input "m" to run mininet console')
    print('input "c" to run custom')
    print('input "g <rate> <size> <protocol>" to generate scripts')
    input_row = input()
    i = input_row.split()
    if len(i) == 1 and i[0] == 'm':
        CLI(net)
    elif i[0] == 'c':
        tt = read_traffic_types()
        host_map = get_host_map(topo.g.node)
        receivers = get_receivers(tt)
        senders = get_senders(tt)
        make_skripts(tt, host_map)
        run_custom(senders, receivers)
    elif i[0] == 'g':
        if len(i) == 1:
            os.system(f'cd {path} && ./deleteLogs.sh')
            generate_scripts(addrs)
            run()
        elif len(i) == 4:
            os.system(f'cd {path} && ./deleteLogs.sh')
            rate, size, protocol = parse_p_args(i)
            generate_scripts(addrs, rate, size, protocol)
            run()
        else:
            print('some args were skipped')
            continue
    elif i[0] == 'k':
        for i in range(1, hosts_num + 1):
            list_of_hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')
    elif i[0] == 'q':
        break

net.stop()
