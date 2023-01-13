from copy import deepcopy
import api
import dijkstra
import matrix


class Path:
    def __init__(self, *args):
        self.list = [x for x in args]


class HostPair:
    def __init__(self, h1, h2):
        self.h1 = h1
        self.h2 = h2

    def get_dst_host_num(self):
        return self.h2[1:]


def get_host_switch_map(hosts):
    h = {}
    for host in hosts:
        h[host["mac"]] = {"switch": host["locations"][0]["elementId"], "ip": host["ipAddresses"][0]}
    return h


def get_host_mac_map(hosts):
    h = {}
    for host in hosts:
        h[host["ipAddresses"][0].split('.')[-1]] = host["mac"]
    return h


def to_onos_device(dev_num: str):
    return "of:" + dev_num.zfill(16)


def to_hex(num: int):
    return f'{num:x}'


def make_intent(points, hosts, links, src_host, dst_host):
    intents = []
    host_mac_map = get_host_mac_map(hosts)
    dst_switch = to_onos_device(to_hex(points.list[len(points.list) - 1]))
    src_switch = to_onos_device(to_hex(points.list[0]))
    print(f"Switches: {src_switch} -> {dst_switch}")
    print(f"Hosts: {src_host} -> {dst_host}")
    ETH_SRC = host_mac_map[str(src_host)]
    print("ETH_SRC ", ETH_SRC)
    ETH_DST = host_mac_map[str(dst_host)]
    print("ETH_DST ", ETH_DST)

    for point in range(0, len(points.list)):
        portIn = ""
        portOut = ""

        deviceId = to_onos_device(to_hex(points.list[point]))
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

        if len(points.list) != 1:
            for link in links:
                if link["src"]["device"] == deviceId and int(link["dst"]["device"][3:], 16) in points.list:
                    if point < 1:
                        intent["ingressPoint"]["port"] = "1"
                        if int(src_host) % 2 == 0:
                            intent["ingressPoint"]["port"] = "2"
                    elif (link["dst"][
                              "device"] == to_onos_device(to_hex(points.list[point - 1]))
                          and points.list[point - 1] in points.list):
                        portIn = link["src"]["port"]
                        intent["ingressPoint"]["port"] = portIn
                    if point + 1 > len(points.list) - 1:
                        intent["egressPoint"]["port"] = "1"
                        if int(dst_host) % 2 == 0:
                            intent["egressPoint"]["port"] = "2"
                    elif (link["dst"][
                              "device"] == to_onos_device(to_hex(points.list[point + 1]))
                          and points.list[point + 1] in points.list):
                        portOut = link["src"]["port"]
                        intent["egressPoint"]["port"] = portOut
                    else:
                        continue

        if len(points.list) == 1:
            intent["ingressPoint"]["port"] = "2"
            intent["egressPoint"]["port"] = "1"
            if int(dst_host) % 2 == 0:
                intent["ingressPoint"]["port"] = "1"
                intent["egressPoint"]["port"] = "2"

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


def hosts_func(hosts):
    h = {}
    for host in hosts:
        h[host["locations"][0]["elementId"]] = {"mac": host["mac"], "ip": host["ipAddresses"][0]}
    return h


def read_all_to_all(hosts: dict):
    length = len(hosts)
    d = {}
    for i in range(1, length + 1):
        d[str(i)] = [str(j) for j in range(1, length + 1) if j != i]
    return d


# def get_src_dst_map(traffic):
#     src_dst_map = {}
#     for pair in traffic[0][1]:
#         if pair[0] not in src_dst_map:
#             src_dst_map[pair[0]] = []
#         src_dst_map[pair[0]].append(pair[1])
#     return src_dst_map


def go_dijkstra(graph: dijkstra.Graph, start: int) -> list:
    graph.print_adj_mat()
    # start = hex(start)[2:]
    # if len(start) < 2:
    #     start = '0' + start
    start = to_onos_device(to_hex(start))
    print(f'start switch: {start}')
    # start_node = graph.get_node_by_data(f"of:00000000000000{start}")
    start_node = graph.get_node_by_data(start)
    print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(start_node)])
    path_list = graph.dijkstra(start_node)
    return path_list


def get_routes_for_each_switch_target(switch_targets: list, paths: list):
    routes = []
    for path in paths:
        points = Path()
        nodes = path[1]
        if int(nodes[-1].data[3:], 16) in switch_targets:
            num_nodes = [int(_.data[3:], 16) for _ in nodes]
            points.list = num_nodes
            routes.append(points)
            print(points.list)
    return routes


def get_intents_to_send(graph: dijkstra.Graph, h, links, src_dst_switch_map: {}, switch_start_pairs: {}) -> dict:
    pair_intents = []
    print(f'src_dst_switch_map: {src_dst_switch_map}')
    for src_switch in src_dst_switch_map:
        start_switch_node = int(src_switch)
        switch_targets = src_dst_switch_map[src_switch]
        paths = go_dijkstra(graph, start_switch_node)
        routes = get_routes_for_each_switch_target(switch_targets, paths)
        print(routes)
        for start_switch in switch_start_pairs:
            for pair in switch_start_pairs[start_switch]:
                for route in routes:
                    if len(route.list) == 1 and route.list[0] == define_switch_on_host(
                            int(pair[0])) == define_switch_on_host(int(pair[1])) or start_switch == \
                            route.list[0] and define_switch_on_host(int(pair[1])) == route.list[-1]:
                        pair_intents.extend(make_intent(route, h, links, pair[0], pair[1]))
                        break
    print("\n")
    # print(json.dumps(pair_intents, indent=4))
    intents = {"intents": pair_intents}
    return intents


def define_switch_on_host(host: int):
    switch = host / 2
    if switch % 2 != 0:
        switch = (host + 1) / 2
    return int(switch)


def get_src_dst_switch_map_reachability_matrix(reachability_matrix, traffic, host_switch_conn):
    """ Возвращает мапу вида: src_switch:[dst_switch1, dst_switch2,...] """
    hosts_pairs_only = traffic[0][1]
    src_dst_switch_map = {}
    for pair in hosts_pairs_only:
        src_switch = host_switch_conn[int(pair[0])]
        dst_switch = host_switch_conn[int(pair[1])]
        if src_switch not in src_dst_switch_map:
            src_dst_switch_map[src_switch] = []
        src_dst_switch_map[src_switch].append(dst_switch)
        # обновляем матрицу достижимости
        reachability_matrix[src_switch][dst_switch] = 1
    print(f"src_dst_switch_map: {src_dst_switch_map}")
    print("Reachability matrix:\n")
    for i in reachability_matrix:
        for j in i:
            print(j, end=' ')
        print()
    return src_dst_switch_map


def get_switch_start_pairs(host_pairs, host_switch_conn):
    start_switch_pairs = {}
    for pair in host_pairs:
        src_host = int(pair[0])
        # определяем свитч, к которому подключен хост
        start_switch = host_switch_conn[src_host]
        if start_switch not in start_switch_pairs:
            start_switch_pairs[start_switch] = []
        start_switch_pairs[start_switch].append(pair)
    return start_switch_pairs


def remove_duplicates(all_traffic):
    """ Преобразует список вида src->dst, dst->src,... в src<->dst..."""
    without_dup = {}
    for pair in all_traffic:
        src, dst = pair[0], pair[1]
        if src not in without_dup:
            without_dup[src] = []
        if dst in without_dup and src in without_dup[dst]:
            continue
        without_dup[src].append(dst)
    res = []
    for src in without_dup:
        for dst in without_dup[src]:
            res.append([src, dst])
    return res


def main():
    links = api.get_links()

    devices = dijkstra.get_devices_list(links)

    nodes = dijkstra.get_nodes(devices)
    print(nodes)

    graph = dijkstra.Graph.create_from_nodes(nodes)

    # -------------------  No weights   -------------------------
    # Common adjacency matrix that tells about the switches connections
    graph.adj_mat = matrix.get_matrix(links, len(devices))
    # ---------------------- Weights  -----------------------
    # graph.adj_mat = input_data.main()

    pair_intents = []
    hosts_list = api.get_hosts()
    # h = hosts_func(hosts_list)
    # hsm = get_host_switch_map(hosts_list)

    # if type == 'c':
    #     src_dst_map = get_src_dst_map(read_custom_traffic)
    # elif type == 'g':
    #     src_dst_map = read_all_to_all(h)

    # d = read_all_to_all(h)
    # if True:
    #     points = Path()
    #     # points.list = [1, 2, 5, 8]
    #     points.list = [1, 4, 6, 8]
    #     routes = []
    #     routes.append(points)
    #     for route in routes:
    #         pair_intents.extend(make_intent(route, h, links))
    # else:
    # src_dst_host_map = {'1': ['2', '4', '6', '8', '10'], '2': ['1', '3', '5', '7', '9'],
    #                     '3': ['2', '4', '6', '8', '10'], '4': ['1', '3', '5', '7', '9'],
    #                     '5': ['2', '4', '6', '8', '10'], '6': ['1', '3', '5', '7', '9'],
    #                     '7': ['2', '4', '6', '8', '10'], '8': ['1', '3', '5', '7', '9'],
    #                     '9': ['2', '4', '6', '8', '10'], '10': ['1', '3', '5', '7', '9']}
    switches_num = 20
    reachability_matrix = [[0] * switches_num for _ in range(switches_num)]
    traffic = [['udp', [['1', '2'], ['1', '4'], ['1', '6'], ['1', '8'], ['1', '10'], ['2', '1'], ['2', '3'], ['2', '5'],
                        ['2', '7'], ['2', '9'], ['3', '2'], ['3', '4'], ['3', '6'], ['3', '8'], ['3', '10'], ['4', '1'],
                        ['4', '3'], ['4', '5'], ['4', '7'], ['4', '9'], ['5', '2'], ['5', '4'], ['5', '6'], ['5', '8'],
                        ['5', '10'], ['6', '1'], ['6', '3'], ['6', '5'], ['6', '7'], ['6', '9'], ['7', '2'], ['7', '4'],
                        ['7', '6'], ['7', '8'], ['7', '10'], ['8', '1'], ['8', '3'], ['8', '5'], ['8', '7'], ['8', '9'],
                        ['9', '2'], ['9', '4'], ['9', '6'], ['9', '8'], ['9', '10'], ['10', '1'], ['10', '3'],
                        ['10', '5'], ['10', '7'], ['10', '9']]]]
    # traffic = [['udp', [['2', '3'], ['3', '2']]]]
    t = remove_duplicates(traffic[0][1])
    host_switch_conn = {}
    with open('/home/andre/PycharmProjects/onos_short_path/core/topologies/fat_tree_hosts.txt', "r") as f:
        for line in f.readlines():
            host, switch = map(int, line.strip().split(", "))
            host_switch_conn[host] = switch
    switch_start_pairs = get_switch_start_pairs(t, host_switch_conn)
    # switch_start_pairs = get_switch_start_pairs(traffic[0][1])
    # print(switch_start_pairs)

    src_dst_switch_map = get_src_dst_switch_map_reachability_matrix(reachability_matrix, traffic, host_switch_conn)
    intents = get_intents_to_send(graph, hosts_list, links, src_dst_switch_map, switch_start_pairs)
    # post_intents(intents)


if __name__ == '__main__':
    main()
