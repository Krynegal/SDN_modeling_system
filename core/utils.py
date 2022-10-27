#!/usr/bin/python
import os

core_path = '/home/andre/PycharmProjects/onos_short_path/core'
scripts_path = core_path + 'scripts/'


def read_traffic_types():
    res = []
    with open(f"{scripts_path}traffic_types.txt", "r") as f:
        for line in f.readlines():
            split_line = line.strip("\n").split(";")
            protocol = split_line[0]
            pairs = [x.strip().split(",") for x in split_line[1:]]
            res.append([protocol, pairs])
    print(res)
    return res


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


def make_scripts(traffic, h_map):
    # check_file = os.path.exists(f'{onos_project_path}script*')
    # if check_file:
    #     os.system(f'cd {onos_project_path} && rm script*')
    os.system(f'cd {scripts_path} && rm script* -f')
    for t in traffic:
        for h in t[1]:
            with open(f"{scripts_path}script{h[0]}", "a") as f:
                f.writelines(f"-a {h_map[h[1]]} -C 1000 -c 500 -T {t[0]}\n")
            os.chmod(rf"{scripts_path}script{h[0]}", 0o777)
