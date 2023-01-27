#!/usr/bin/python

core_path = '/home/andre/PycharmProjects/onos_short_path/core'
scripts_path = core_path + 'scripts/'
USER = ("onos", "rocks")


def get_host_addr_map(topo_modes):
    m = {}
    for node in topo_modes:
        if 'ip' in topo_modes[node]:
            m[node[1:]] = topo_modes[node]['ip']
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
