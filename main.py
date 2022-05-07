import requests as req
import json
import dijkstra
import input_data
import matrix


def get_ip():
    with open("D:/Scripts/vmIP.txt", "r") as f:
        ip = f.readline().strip()
    return ip


USER = ("onos", "rocks")


# IP = get_ip()


def get_links():
    res = req.get(f"http://{IP}:8181/onos/v1/links", auth=USER)
    links = res.json()["links"]
    with open("topology_links.json", "w") as f:
        f.write(json.dumps(res.json(), indent=4))
    # print(json.dumps(res.json(), indent=4))
    return links


class Path:
    def __init__(self, *args):
        self.list = [x for x in args]


class HostPair:
    def __init__(self, h1, h2):
        self.h1 = h1
        self.h2 = h2


def get_points(path_list):
    for list in path_list:
        nodes = list[1]
        if nodes[-1].data[-1] == host_pair.h2[-1]:
            num_nodes = [int(_.data[-1]) for _ in nodes]
            points = Path()
            points.list = num_nodes
            print()
    return points


def make_intent(points, links):
    intents = []
    for point in range(0, len(points.list)):
        portIn = ""
        portOut = ""
        deviceId = f"of:000000000000000{points.list[point]}"
        intent = {
            "type": "PointToPointIntent",
            "appId": "org.onosproject.cli",
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
            if link["src"]["device"] == deviceId and int(link["dst"]["device"][-1]) in points.list:
                if point < 1:
                    intent["ingressPoint"]["port"] = "1"
                if (link["dst"]["device"] == f"of:000000000000000{points.list[point - 1]}"
                        and points.list[point - 1] in points.list):
                    portIn = link["src"]["port"]
                    intent["ingressPoint"]["port"] = portIn
                if point + 1 > len(points.list) - 1:
                    intent["egressPoint"]["port"] = "1"
                elif (link["dst"]["device"] == f"of:000000000000000{points.list[point + 1]}"
                      and points.list[point + 1] in points.list):
                    portOut = link["src"]["port"]
                    intent["egressPoint"]["port"] = portOut
                else:
                    continue
        intents.append(intent)
        continue
    return intents


def post_intents(data):
    for intent in data["intents"]:
        res = req.post(f"http://{IP}:8181/onos/v1/intents", json=intent, auth=USER)
    print(res)


def get_devices_list(links) -> list:
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


if __name__ == '__main__':
    IP = get_ip()

    links = get_links()

    devices = get_devices_list(links)

    nodes = get_nodes(devices)
    print(nodes)

    graph = dijkstra.Graph.create_from_nodes(nodes)

    #################### No weights ######################
    # Common adjacency matrix that tells us about the switches connections
    # graph.adj_mat = matrix.get_matrix(links, len(devices))
    ##################### Weights ########################
    graph.adj_mat = input_data.main()

    graph.print_adj_mat()
    start_node = graph.get_node_by_data("of:0000000000000001")
    print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(start_node)])
    path_list = graph.dijkstra(start_node)

    #####################################################################

    host_pair = HostPair("h1", "h6")
    points = get_points(path_list)

    intents = {"intents": []}
    intents["intents"] = make_intent(points, links)

    points.list.reverse()
    intents["intents"].extend(make_intent(points, links))
    data = intents
    print("\n")
    print(json.dumps(data, indent=4))
