#!/usr/bin/python

import time

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
import os
from mininet.node import OVSSwitch, RemoteController

net = Mininet()

c0 = net.addController('c0', controller=RemoteController, ip='172.17.0.2', port=6653)


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
        with open("nodes.txt", "r") as f:
            for line in f.readlines():
                nodes.extend(line.strip().split(", "))
        nodes = list(set(nodes))
        nodes.sort()
        # print(nodes)

        for i in range(len(nodes)):
            nodes[i] = Node(nodes[i])
        # print(nodes)

        graph = Graph.create_from_nodes(nodes)

        matrix = [[0] * len(nodes) for _ in range(len(nodes))]
        with open("nodes.txt", "r") as f:
            for line in f.readlines():
                src, dst = map(int, line.strip().split(", "))
                matrix[src - 1][dst - 1] = 1
                matrix[dst - 1][src - 1] = 1

        graph.adj_mat = matrix

        hosts = []
        switches = []
        for i in range(len(graph.nodes)):
            switches.append(self.addSwitch('s' + graph.nodes[i].data))
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
time.sleep(3)
net.pingAll()
time.sleep(3)

CLI(net)
