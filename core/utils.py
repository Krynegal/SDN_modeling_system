#!/usr/bin/python
import requests as req

core_path = '/home/andre/PycharmProjects/onos_short_path/core'
scripts_path = core_path + 'scripts/'
USER = ("onos", "rocks")


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


def fwd_activate(activate: bool):
    if activate:
        res = req.post("http://172.17.0.2:8181/onos/v1/applications/org.onosproject.fwd/active", auth=USER)
        if res.status_code == 200:
            print('fwd is on')
    else:
        res = req.delete("http://172.17.0.2:8181/onos/v1/applications/org.onosproject.fwd/active", auth=USER)
        if res.status_code == 204:
            print('fwd is off')
