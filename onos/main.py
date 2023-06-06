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


def to_onos_device(dev_num: str):
    return "of:" + dev_num.zfill(16)


def to_hex(num: int):
    return f'{num:x}'


def make_intent(points, hosts_info, links, src_host, dst_host):
    intents = []
    dst_switch = to_onos_device(to_hex(points.list[len(points.list) - 1]))
    src_switch = to_onos_device(to_hex(points.list[0]))
    print(f"Switches: {src_switch} -> {dst_switch}")
    print(f"Hosts: {src_host} -> {dst_host}")
    ETH_SRC = hosts_info[str(src_host)]["mac"]
    print("ETH_SRC ", ETH_SRC)
    ETH_DST = hosts_info[str(dst_host)]["mac"]
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
                        intent["ingressPoint"]["port"] = hosts_info[src_host]["port"]
                    elif (link["dst"]["device"] == to_onos_device(to_hex(points.list[point - 1]))
                          and points.list[point - 1] in points.list):
                        portIn = link["src"]["port"]
                        intent["ingressPoint"]["port"] = portIn
                    if point + 1 > len(points.list) - 1:
                        intent["egressPoint"]["port"] = hosts_info[dst_host]["port"]
                    elif (link["dst"]["device"] == to_onos_device(to_hex(points.list[point + 1]))
                          and points.list[point + 1] in points.list):
                        portOut = link["src"]["port"]
                        intent["egressPoint"]["port"] = portOut
                    else:
                        continue

        if len(points.list) == 1:
            intent["ingressPoint"]["port"] = hosts_info[src_host]["port"]
            intent["egressPoint"]["port"] = hosts_info[dst_host]["port"]

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


def read_all_to_all(hosts: dict):
    length = len(hosts)
    d = {}
    for i in range(1, length + 1):
        d[str(i)] = [str(j) for j in range(1, length + 1) if j != i]
    return d


def go_dijkstra(graph: dijkstra.Graph, start: int) -> list:
    graph.print_adj_mat()
    start = to_onos_device(to_hex(start))
    print(f'start switch: {start}')
    start_node = graph.get_node_by_data(start)
    print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(start_node)])
    path_list = graph.dijkstra(start_node)
    return path_list


def get_routes_for_each_switch_target(graph: dijkstra.Graph, switch_targets: list, paths: list):
    routes = []
    for path in paths:
        points = Path()
        nodes = path[1]
        if int(nodes[-1].data[3:], 16) in switch_targets:
            num_nodes = [int(_.data[3:], 16) for _ in nodes]
            
            for i in range(len(num_nodes)-1):
                src = num_nodes[i]
                dst = num_nodes[i+1]
                old_weight = graph.get_weight(src-1, dst-1)
                if old_weight != 0:
                    new_weight = old_weight+0.01
                    print(f'src: {src}; dst: {dst}; old_weight: {old_weight}; new_weight: {new_weight}')
                    graph.set_new_weight(src, dst, new_weight)
            
            points.list = num_nodes
            routes.append(points)
            print(f'points.list {points.list}')
    return routes


def get_intents_to_send(graph: dijkstra.Graph, hosts_info, links, src_dst_switch_map: {},
                        switch_start_pairs: {}) -> dict:
    pair_intents = []
    print(f'src_dst_switch_map: {src_dst_switch_map}')
    for src_switch in src_dst_switch_map:
        start_switch_node = int(src_switch)
        switch_targets = src_dst_switch_map[src_switch]
        switch_targets = list(set(switch_targets))
        paths = go_dijkstra(graph, start_switch_node)
        routes = get_routes_for_each_switch_target(graph, switch_targets, paths)
        print(f'routes: {routes}')
        for start_switch in switch_start_pairs:
            for pair in switch_start_pairs[start_switch]:
                for route in routes:
                    if len(route.list) == 1 and route.list[0] == hosts_info[pair[0]]["switch"] == \
                            hosts_info[pair[1]]["switch"] or start_switch == route.list[0] and \
                            hosts_info[pair[1]]["switch"] == route.list[-1]:
                        pair_intents.extend(make_intent(route, hosts_info, links, pair[0], pair[1]))
                        break
    print("\n")
    # print(json.dumps(pair_intents, indent=4))
    intents = {"intents": pair_intents}
    return intents


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


def get_hosts_info(hosts):
    hosts_info = {}
    for host in hosts:
        locations = host["locations"][0]
        hosts_info[host["ipAddresses"][0].split('.')[-1]] = {
            "mac": host["mac"],
            "port": locations["port"],
            "switch": int(locations["elementId"][3:], 16),
            "onos_switch": locations["elementId"],
        }
    return hosts_info


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

    hosts_list = api.get_hosts()
    hosts_info = get_hosts_info(hosts_list)

    switches_num = 20
    reachability_matrix = [[0] * switches_num for _ in range(switches_num)]
    # traffic = [['udp', [['1', '2'], ['1', '4'], ['1', '6'], ['1', '8'], ['1', '10'], ['2', '1'], ['2', '3'], ['2', '5'],
    #                     ['2', '7'], ['2', '9'], ['3', '2'], ['3', '4'], ['3', '6'], ['3', '8'], ['3', '10'], ['4', '1'],
    #                     ['4', '3'], ['4', '5'], ['4', '7'], ['4', '9'], ['5', '2'], ['5', '4'], ['5', '6'], ['5', '8'],
    #                     ['5', '10'], ['6', '1'], ['6', '3'], ['6', '5'], ['6', '7'], ['6', '9'], ['7', '2'], ['7', '4'],
    #                     ['7', '6'], ['7', '8'], ['7', '10'], ['8', '1'], ['8', '3'], ['8', '5'], ['8', '7'], ['8', '9'],
    #                     ['9', '2'], ['9', '4'], ['9', '6'], ['9', '8'], ['9', '10'], ['10', '1'], ['10', '3'],
    #                     ['10', '5'], ['10', '7'], ['10', '9']]]]
    traffic = [["UDP", [["2","10"], ["1","5"]]]]
    # traffic = [['UDP',
    #   [['1', '2'], ['1', '3'], ['1', '4'], ['1', '5'], ['1', '6'], ['1', '7'], ['1', '8'], ['1', '9'], ['1', '10'],
    #    ['1', '11'], ['1', '12'], ['1', '13'], ['1', '14'], ['1', '15'], ['1', '16'], ['2', '1'], ['2', '3'], ['2', '4'],
    #    ['2', '5'], ['2', '6'], ['2', '7'], ['2', '8'], ['2', '9'], ['2', '10'], ['2', '11'], ['2', '12'], ['2', '13'],
    #    ['2', '14'], ['2', '15'], ['2', '16'], ['3', '1'], ['3', '2'], ['3', '4'], ['3', '5'], ['3', '6'], ['3', '7'],
    #    ['3', '8'], ['3', '9'], ['3', '10'], ['3', '11'], ['3', '12'], ['3', '13'], ['3', '14'], ['3', '15'],
    #    ['3', '16'], ['4', '1'], ['4', '2'], ['4', '3'], ['4', '5'], ['4', '6'], ['4', '7'], ['4', '8'], ['4', '9'],
    #    ['4', '10'], ['4', '11'], ['4', '12'], ['4', '13'], ['4', '14'], ['4', '15'], ['4', '16'], ['5', '1'],
    #    ['5', '2'], ['5', '3'], ['5', '4'], ['5', '6'], ['5', '7'], ['5', '8'], ['5', '9'], ['5', '10'], ['5', '11'],
    #    ['5', '12'], ['5', '13'], ['5', '14'], ['5', '15'], ['5', '16'], ['6', '1'], ['6', '2'], ['6', '3'], ['6', '4'],
    #    ['6', '5'], ['6', '7'], ['6', '8'], ['6', '9'], ['6', '10'], ['6', '11'], ['6', '12'], ['6', '13'], ['6', '14'],
    #    ['6', '15'], ['6', '16'], ['7', '1'], ['7', '2'], ['7', '3'], ['7', '4'], ['7', '5'], ['7', '6'], ['7', '8'],
    #    ['7', '9'], ['7', '10'], ['7', '11'], ['7', '12'], ['7', '13'], ['7', '14'], ['7', '15'], ['7', '16'],
    #    ['8', '1'], ['8', '2'], ['8', '3'], ['8', '4'], ['8', '5'], ['8', '6'], ['8', '7'], ['8', '9'], ['8', '10'],
    #    ['8', '11'], ['8', '12'], ['8', '13'], ['8', '14'], ['8', '15'], ['8', '16'], ['9', '1'], ['9', '2'], ['9', '3'],
    #    ['9', '4'], ['9', '5'], ['9', '6'], ['9', '7'], ['9', '8'], ['9', '10'], ['9', '11'], ['9', '12'], ['9', '13'],
    #    ['9', '14'], ['9', '15'], ['9', '16'], ['10', '1'], ['10', '2'], ['10', '3'], ['10', '4'], ['10', '5'],
    #    ['10', '6'], ['10', '7'], ['10', '8'], ['10', '9'], ['10', '11'], ['10', '12'], ['10', '13'], ['10', '14'],
    #    ['10', '15'], ['10', '16'], ['11', '1'], ['11', '2'], ['11', '3'], ['11', '4'], ['11', '5'], ['11', '6'],
    #    ['11', '7'], ['11', '8'], ['11', '9'], ['11', '10'], ['11', '12'], ['11', '13'], ['11', '14'], ['11', '15'],
    #    ['11', '16'], ['12', '1'], ['12', '2'], ['12', '3'], ['12', '4'], ['12', '5'], ['12', '6'], ['12', '7'],
    #    ['12', '8'], ['12', '9'], ['12', '10'], ['12', '11'], ['12', '13'], ['12', '14'], ['12', '15'], ['12', '16'],
    #    ['13', '1'], ['13', '2'], ['13', '3'], ['13', '4'], ['13', '5'], ['13', '6'], ['13', '7'], ['13', '8'],
    #    ['13', '9'], ['13', '10'], ['13', '11'], ['13', '12'], ['13', '14'], ['13', '15'], ['13', '16'], ['14', '1'],
    #    ['14', '2'], ['14', '3'], ['14', '4'], ['14', '5'], ['14', '6'], ['14', '7'], ['14', '8'], ['14', '9'],
    #    ['14', '10'], ['14', '11'], ['14', '12'], ['14', '13'], ['14', '15'], ['14', '16'], ['15', '1'], ['15', '2'],
    #    ['15', '3'], ['15', '4'], ['15', '5'], ['15', '6'], ['15', '7'], ['15', '8'], ['15', '9'], ['15', '10'],
    #    ['15', '11'], ['15', '12'], ['15', '13'], ['15', '14'], ['15', '16'], ['16', '1'], ['16', '2'], ['16', '3'],
    #    ['16', '4'], ['16', '5'], ['16', '6'], ['16', '7'], ['16', '8'], ['16', '9'], ['16', '10'], ['16', '11'],
    #    ['16', '12'], ['16', '13'], ['16', '14'], ['16', '15']]]]
    # traffic = read_custom_traffic("/home/andre/PycharmProjects/onos_short_path/core/custom_traffic.txt")
    t = remove_duplicates(traffic[0][1])
    host_switch_conn = {}
    with open('/home/andre/PycharmProjects/onos_short_path/core/topologies/fat_tree_hosts.txt', "r") as f:
        for line in f.readlines():
            host, switch = map(int, line.strip().split(", "))
            host_switch_conn[host] = switch
    switch_start_pairs = get_switch_start_pairs(t, host_switch_conn)

    src_dst_switch_map = get_src_dst_switch_map_reachability_matrix(reachability_matrix, traffic, host_switch_conn)
    intents = get_intents_to_send(graph, hosts_info, links, src_dst_switch_map, switch_start_pairs)
    #api.post_intents(intents)


if __name__ == '__main__':
    main()
