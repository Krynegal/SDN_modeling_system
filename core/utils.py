#!/usr/bin/python
import os

core_path = '/home/andre/PycharmProjects/onos_short_path/core'
scripts_path = core_path + 'scripts/'


def host_addr_map(topo):
    g_nodes = topo.g.node
    m = {}
    for node in g_nodes:
        if 'ip' in g_nodes[node]:
            m[node[1:]] = g_nodes[node]['ip']
    print(f'host_addr_map: {m}\n')
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
