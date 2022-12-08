import sys
from copy import deepcopy
from itertools import combinations

import requests
import requests as req
import json

import deleteIntents
import dijkstra
import matrix


def get_ip():
    return "172.17.0.2"


USER = ("onos", "rocks")


def get_links():
    try:
        res = req.get(f"http://{IP}:8181/onos/v1/links", auth=USER)
        links = res.json()["links"]
        with open("../jsonFiles/topology_links.json", "w") as f:
            f.write(json.dumps(res.json(), indent=4))
        print(json.dumps(res.json(), indent=4))
        return links
    except requests.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()


class Path:
    def __init__(self, *args):
        self.list = [x for x in args]


class HostPair:
    def __init__(self, h1, h2):
        self.h1 = h1
        self.h2 = h2

    def get_dst_host_num(self):
        return self.h2[1:]


def make_intent(points, hosts, links):
    intents = []
    dst = f"of:000000000000000{hex(points.list[len(points.list) - 1])[2:]}"
    src = f"of:000000000000000{hex(points.list[0])[2:]}"
    print(f"{src} -> {dst}")
    ETH_SRC = hosts[src]["mac"]
    print("ETH_SRC ", ETH_SRC)
    ETH_DST = hosts[dst]["mac"]
    print("ETH_DST ", ETH_DST)

    for point in range(0, len(points.list)):
        portIn = ""
        portOut = ""

        deviceId = f"of:000000000000000{hex(points.list[point])[2:]}"
        intent = {
            "type": "PointToPointIntent",
            "appId": "org.onosproject.cli",
            "selector": {
                "criteria": [
                    {
                        "type": "ETH_DST",
                        "mac": ETH_DST
                    }
                ]
            },
            "treatment": {
                "instructions": [
                    {
                        "type": "L2MODIFICATION",
                        "subtype": "ETH_SRC",
                        "mac": ETH_SRC
                    }
                ],
                "deferred": []
            },
            "priority": 100,
            "ingressPoint": {
                "port": f"{portIn}",
                "device": deviceId
            },
            "egressPoint": {
                "port": f"{portOut}",
                "device": deviceId
            }
        }
        for link in links:
            if link["src"]["device"] == deviceId and int(link["dst"]["device"][-1], 16) in points.list:
                if point < 1:
                    intent["ingressPoint"]["port"] = "1"
                elif (link["dst"]["device"] == f"of:000000000000000{hex(points.list[point - 1])[2:]}"
                      and points.list[point - 1] in points.list):
                    portIn = link["src"]["port"]
                    intent["ingressPoint"]["port"] = portIn
                if point + 1 > len(points.list) - 1:
                    intent["egressPoint"]["port"] = "1"
                elif (link["dst"]["device"] == f"of:000000000000000{hex(points.list[point + 1])[2:]}"
                      and points.list[point + 1] in points.list):
                    portOut = link["src"]["port"]
                    intent["egressPoint"]["port"] = portOut
                else:
                    continue
        intents.append(intent)
        reversed_intent = reverse_intent(intent)
        intents.append(reversed_intent)
        continue
    return intents


def reverse_intent(intent_old):
    int_new = deepcopy(intent_old)
    int_new["selector"]["criteria"][0]["mac"], int_new["treatment"]["instructions"][0]["mac"] = \
        int_new["treatment"]["instructions"][0]["mac"], int_new["selector"]["criteria"][0]["mac"]
    int_new["ingressPoint"]["port"], int_new["egressPoint"]["port"] = \
        int_new["egressPoint"]["port"], int_new["ingressPoint"]["port"]
    int_new["ingressPoint"]["device"], int_new["egressPoint"]["device"] = \
        int_new["egressPoint"]["device"], int_new["ingressPoint"]["device"]
    return int_new


def post_intents(data):
    intents_num = len(data["intents"])
    successful_requests = 0
    for intent in data["intents"]:
        res = req.post(f"http://{IP}:8181/onos/v1/intents", json=intent, auth=USER)
        if res.status_code == 201:
            successful_requests += 1
    if successful_requests == intents_num:
        print(f"{successful_requests}/{intents_num} were successfully sent")
    else:
        print(f"Oops. Only {successful_requests}/{intents_num} were successfully sent")


def post_flows(data):
    res = req.post(f"http://{IP}:8181/onos/v1/flows", json=data, auth=USER)
    if res.status_code == 200:
        print("flows were successfully send")
    else:
        print("some problem occured while sending flows")


def get_devices_list(links):
    devices = []
    for link in links:
        devices.append(link["src"]["device"])
    devices = list(set(devices))
    devices.sort()
    return devices


def get_nodes(devices):
    nodes = []
    for device in devices:
        nodes.append(dijkstra.Node(device))
    return nodes


def get_hosts():
    try:
        res = req.get(f"http://172.17.0.2:8181/onos/v1/hosts", auth=USER)
        hosts = res.json()["hosts"]
        with open("../jsonFiles/topology_hosts.json", "w") as f:
            f.write(json.dumps(res.json(), indent=4))
        # print(json.dumps(res.json(), indent=4))
        return hosts
    except req.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()


def hosts(hosts):
    h = {}
    for host in hosts:
        h[host["locations"][0]["elementId"]] = {"mac": host["mac"], "ip": host["ipAddresses"][0]}
    return h


def read_custom_traffic():
    res = []
    core_path = '/home/andre/PycharmProjects/onos_short_path/core/'
    custom_t_file_path = core_path + 'custom_traffic.txt'
    with open(f"{custom_t_file_path}", "r") as f:
        for line in f.readlines():
            split_line = line.strip("\n").split(";")
            protocol = split_line[0]
            pairs = [x.strip().split(",") for x in split_line[1:]]
            res.append([protocol, pairs])
    print('custom traffic:', res)
    return res


def read_all_to_all(hosts: dict):
    l = len(hosts)
    d = {}
    for i in range(1, l+1):
        d[str(i)] = [str(j) for j in range(1, l+1) if j != i]
    return d


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


def get_src_dst_map(func):
    traffic = func()
    src_dst_map = {}
    for pair in traffic[0][1]:
        if pair[0] not in src_dst_map:
            src_dst_map[pair[0]] = []
        src_dst_map[pair[0]].extend(pair[1])
    print(src_dst_map)
    return src_dst_map


def go_dijkstra(start: int) -> list:
    graph.print_adj_mat()
    start = hex(start)[2:]
    start_node = graph.get_node_by_data(f"of:000000000000000{start}")
    print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(start_node)])
    path_list = graph.dijkstra(start_node)
    return path_list


def get_routes_for_each_target(targets: list, paths: list) -> [list]:
    routes = []
    for path in paths:
        points = Path()
        nodes = path[1]
        if nodes[-1].data[-1] in targets:
            num_nodes = [int(_.data[-1], 16) for _ in nodes]
            points.list = num_nodes
            routes.append(points)
            print("points", points.list)
    return routes


if __name__ == '__main__':
    type = input('Enter "c" for custom\nEnter "g" for all-to-all')

    IP = get_ip()

    links = get_links()

    devices = get_devices_list(links)

    nodes = get_nodes(devices)
    print(nodes)

    graph = dijkstra.Graph.create_from_nodes(nodes)

    #################### No weights ######################
    # Common adjacency matrix that tells about the switches connections
    graph.adj_mat = matrix.get_matrix(links, len(devices))
    ##################### Weights ########################
    # graph.adj_mat = input_data.main()

    pair_intents = []
    hosts_list = get_hosts()
    h = hosts(hosts_list)

    if type == 'c':
        src_dst_map = get_src_dst_map(read_custom_traffic)
    elif type == 'g':
        src_dst_map = read_all_to_all(h)

    #d = read_all_to_all(h)

    for src in src_dst_map:
        start_node = int(src)
        targets = src_dst_map[src]
        paths = go_dijkstra(start_node)
        routes = get_routes_for_each_target(targets, paths)
        for route in routes:
            pair_intents.extend(make_intent(route, h, links))

    print("\n")
    print(json.dumps(pair_intents, indent=4))

    deleteIntents.clear()
    intents = {"intents": pair_intents}
    post_intents(intents)

    # while True:
    #     src, dst, w = map(int, input("Input src, dst, w:\n").split())
    #     if graph.set_new_weight(src, dst, w):
    #         path_list = graph.dijkstra(start_node)
    #         print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(start_node)])
    #
    #         points = get_points(path_list, host_pair)
    #         print(points.list)
    #
    #         intents = {"intents": make_intent(points, h, links)}
    #         points.list.reverse()
    #         intents["intents"].extend(make_intent(points, h, links))
    #
    #         deleteIntents.clear()
    #         post_intents(intents)
