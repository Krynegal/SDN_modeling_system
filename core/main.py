#!/usr/bin/python
import os
import sys
import time
from datetime import datetime
from threading import Thread

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import RemoteController, OVSSwitch

conf_path = os.getcwd()
sys.path.append("/home/andrey/SDN_modeling_system/onos")
sys.path.append("/home/andrey/.local/lib/python3.8/site-packages")
sys.path.append("..")
sys.path.append(conf_path)
print(sys.path)

from core.read_scenario import read_scenario, find_max_flow_duration
from utils import get_host_addr_map, get_receivers, get_senders
from scripters import generate_custom, read_custom_traffic
from runners import run_custom, run_stats_processing
from onos.main import get_intents_to_send, get_switch_start_pairs, get_src_dst_switch_map_reachability_matrix, \
    remove_duplicates, to_onos_device, to_hex
from onos.dijkstra import get_dijkstra_graph
from onos.stats import read_weights_matrix

from onos.api import post_intents, get_links, arp_on

from configs.configs import core_path, itg_path, VM, IP, used_onos_controllers


scenario = read_scenario()
controllers_number = scenario["controllers_number"]
bandwidth = scenario["bandwidth"]
topo_file = '/topologies/' + scenario["topo_file_path"]
switch_hosts_conn_file = '/topologies/' + scenario["switch_hosts_conn_file_path"]
switch_controller_file = scenario["switch_controller_file_path"]
topo_path = core_path + topo_file
topo_path_hosts = core_path + switch_hosts_conn_file


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
        nodes = []
        adjacency_list = {}
        with open(topo_path, "r") as f:
            for line in f.readlines():
                splited_line = line.strip().split(", ")
                nodes.extend(splited_line)
                src, dst = map(int, splited_line)
                if src not in adjacency_list.keys():
                    adjacency_list[src] = []
                adjacency_list[src].append(dst)

        nodes = list(set(nodes))
        nodes.sort(key=int)
        print(nodes)
        for i in range(len(nodes)):
            nodes[i] = Node(nodes[i])

        graph = Graph.create_from_nodes(nodes)

        # мапа хост : свитч
        host_switch_conn = {}
        with open(topo_path_hosts, "r") as f:
            for line in f.readlines():
                host, switch = map(int, line.strip().split(", "))
                host_switch_conn[host] = switch

        # матрица соединений свитчей
        matrix = [[0] * len(nodes) for _ in range(len(nodes))]
        for src in adjacency_list:
            for dst in adjacency_list[src]:
                matrix[src - 1][dst - 1] = 1
                matrix[dst - 1][src - 1] = 1

        graph.adj_mat = matrix
        switches = []
        print('len(graph.nodes): ', len(graph.nodes))
        # создаем все свитчи
        for i in range(len(graph.nodes)):
            switches.append(self.addSwitch('s' + graph.nodes[i].data, protocols="OpenFlow13"))
        # создаем все хосты и коннектим их с их свитчами
        for host_num in host_switch_conn:
            host = self.addHost(f'h{host_num}', ip=f'192.168.{host_num // 255}.{host_num % 255 + (host_num // 255)}')
            if bandwidth == 1000:
                self.addLink(host, switches[host_switch_conn[host_num] - 1], bw=1000)
            else:
                self.addLink(host, switches[host_switch_conn[host_num] - 1], bw=1000)
                
        # add links between switches
        for row in range(len(graph.adj_mat)):
            for col in range(row, len(graph.adj_mat[row])):
                if graph.adj_mat[row][col] != 0:
                    if bandwidth == 1000:
                        self.addLink(switches[row], switches[col], bw=1000)
                    else:
                        self.addLink(switches[row], switches[col])


def delete_old_files():
    os.system(f'cd {itg_path} && rm -f *.log')
    os.system(f'cd {itg_path} && rm -f *.dat')
    os.system(f'cd {itg_path} && rm -f *.txt')


def read_switch_controller_file() -> dict:
    with open(switch_controller_file, "r") as f:
        lines = f.readlines()
    switch_controller = {}
    for line in lines:
        switch_num, controller_num = line.strip().split(', ')
        switch_controller[switch_num] = controller_num
    return switch_controller


def get_number_of_controllers(switch_controller: dict) -> int:
    return len(set(switch_controller.values()))


def get_cmap(switch_controller: dict, controllers: list) -> dict:
    cmap = {}
    for switch in switch_controller:
        cmap[f's{switch}'] = controllers[int(switch_controller[switch]) - 1]
    return cmap


# def gen_host_switch_pair():
#     h_num = 1
#     with open(f"{core_path}/topologies/fat_tree_hosts_test.txt", "w") as f:
#         for s in range(1, 8 + 1):
#             for h in range(1, 24 + 1):
#                 f.write(f'{h_num}, {s}\n')
#                 h_num += 1
def gen_host_switch_pair():
    h_num = 1
    with open(f"{core_path}/topologies/fat_tree_hosts_100.txt", "w") as f:
        for s in range(1, 40 + 1):
            for h in range(1, 5 + 1):
                f.write(f'{h_num}, {s}\n')
                h_num += 1


def get_hosts_info_2(net):
    hosts_info = {}
    with open(f"{topo_path_hosts}", "r") as f:
        lines = f.readlines()
        lastSwitchNum = ""
        for line in lines:
            h, s = line.strip().split(', ')
            if s != lastSwitchNum:
                port_num = 0
                lastSwitchNum = s
            port_num += 1
            net_host = net.get(f'h{h}')
            res = net_host.cmd("ifconfig | awk 'FNR==2||FNR==4{print $2}'")
            ip, mac = [x.strip() for x in res.split("\n")][:2]
            port = str(port_num)
            switch = int(s)
            onos_switch = to_onos_device(to_hex(switch))
            hosts_info[h] = {
                "mac": mac,  # string
                "port": port,  # string
                "switch": switch,  # int, example: 1..192
                "onos_switch": onos_switch,  # string of:00000000000000a
            }
    return hosts_info


def get_onos_ips(onos_names: list) -> list:
    onos_ips = []
    for name in onos_names:
        ip = os.popen(f"docker inspect -f '{{{{range.NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' {name}").read()
        onos_ips.append(ip.strip())
    return onos_ips


def main():
    # gen_host_switch_pair()

    switch_ctrls = read_switch_controller_file()
    
    onos_ips = get_onos_ips(used_onos_controllers)
    
    print(f'VM {VM}')
    print(f'IP: {IP}')
    print(f'c_num {controllers_number}')
    if VM:
        onos_ips = [IP]*controllers_number
    print(f'onos_ips: {onos_ips}')
    ctrls = []
    port = 6653
    for i in range(len(onos_ips)):
        c = RemoteController(f'c{i+1}', ip=f'{onos_ips[i]}', port=port)
        ctrls.append(c)
        port += 1
    
    cmap = get_cmap(switch_ctrls, ctrls)
    print(f'cmap: {cmap}')

    class MultiSwitch(OVSSwitch):
        def start(self, controllers):
            return OVSSwitch.start(self, [cmap[self.name]])

    topo = MyTopo()
    net = Mininet(topo=topo, switch=MultiSwitch, build=False, link=TCLink)
    for c in ctrls:
        net.addController(c)
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
    arp_on()
    while True:
        print('input "m" to run mininet console')
        print('input "c" to run custom')
        input_line = input().split()
        if len(input_line) == 1 and input_line[0] == 'm':
            CLI(net)
        elif input_line[0] == 'c':
            # чистим файлы, оставшиеся после прошлых запусков
            delete_old_files()
            os.system(f'rm -rf {core_path}/actions/*')

            # строим граф, который будем использовать для поиска путей минимальной стоимости
            links = get_links()
            graph = get_dijkstra_graph(links)

            hosts_info = get_hosts_info_2(net)
            print(f"hosts_info: {hosts_info}")

            # матрица достижимости для свитчей
            reachability_matrix = [[0] * switches_num for _ in range(switches_num)]

            threads = []
            all_receivers = []
            scenario = read_scenario()
            max_flow_duration = find_max_flow_duration(scenario)
            for flow in scenario['flows']:
                # получаем информацию об очередном потоке
                id = flow['id']
                start_time = flow['start_time']
                traffic_conf = flow['traffic_conf']
                print(f"{flow['id']} in cycle! sleep {start_time} seconds")
                time.sleep(start_time)

                # получаем трафик, который будет передаваться в потоке
                custom_t_file_path = core_path + '/custom_traffics/' + flow['name']
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
                        graph.adj_mat = read_weights_matrix(id)
                    intents = get_intents_to_send(graph, hosts_info, links, src_dst_switch_map, switch_start_pairs)
                    post_intents(intents)
                else:
                    print("src_dst_map is empty. There are no new intents")

                receivers = get_receivers(traffic)
                senders = get_senders(traffic)
                generate_custom(id, host_addr_map, traffic, traffic_conf)

                if id == 1:
                    time.sleep(20)
                    stat_thread = Thread(name="stats thread", target=run_stats_processing,
                                         args=(links, switches_num, max_flow_duration, switch_controller_file, bandwidth))
                    stat_thread.start()
                    print(f'thread: {stat_thread.name} is started at {datetime.now().strftime("%H:%M:%S")}')
                    threads.append(stat_thread)

                scripts_path = core_path + f'/actions/action{id}/'
                name = str(id)
                thread = Thread(name=name, target=run_custom,
                                args=(
                                    scripts_path, hosts, senders, receivers, all_receivers, traffic_conf["duration"],))
                thread.start()
                print(f'thread: {thread.name} is started at {datetime.now().strftime("%H:%M:%S")}')
                threads.append(thread)

            for thread in threads:
                print(f'thread {thread} is STOPPED at {datetime.now().strftime("%H:%M:%S")}')
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
