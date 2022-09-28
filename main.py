import sys

import requests
import requests as req
import json

import deleteIntents
import dijkstra
import input_data
import matrix


def get_ip():
    # with open("D:/Scripts/vmIP.txt", "r") as f:
    #     ip = f.readline().strip()
    return "172.17.0.2"


USER = ("onos", "rocks")


def get_links():
    try:
        res = req.get(f"http://{IP}:8181/onos/v1/links", auth=USER)
        links = res.json()["links"]
        with open("topology_links.json", "w") as f:
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


def get_points(path_list):
    points = Path()
    for list in path_list:
        nodes = list[1]
        if nodes[-1].data[-1] == hex(int(host_pair.get_dst_host_num()))[2:]:
            num_nodes = [int(_.data[-1], 16) for _ in nodes]
            points.list = num_nodes
            print()
    return points


def make_intent(points, links, reversed):
    intents = []
    for point in range(0, len(points.list)):
        portIn = ""
        portOut = ""

        ETH_DST = "56:57:EF:56:2E:45"
        ETH_SRC = "DA:D8:AB:5C:5D:6C"
        #  "6A:F9:1C:DB:20:2D" 1 host
        if reversed:
            ETH_DST, ETH_SRC = ETH_SRC, ETH_DST

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
                if (link["dst"]["device"] == f"of:000000000000000{hex(points.list[point - 1])[2:]}"
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
        continue
    return intents


def post_intents(data):
    intents_num = len(data["intents"])
    successful_requests = 0
    for intent in data["intents"]:
        res = req.post(f"http://{IP}:8181/onos/v1/intents", json=intent, auth=USER)
        if res.status_code == 200:
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
        with open("topology_hosts.json", "w") as f:
            f.write(json.dumps(res.json(), indent=4))
        #print(json.dumps(res.json(), indent=4))
        return hosts
    except req.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()

def hosts(hosts):
    h = {}
    for host in hosts:
        h[host["locations"][0]["elementId"]] = {"mac": host["mac"], "ip": host["ipAddresses"][0]}
    return h

def revert_flow(flow):
    flow["treatment"]["instructions"][0]["port"], flow["selector"]["criteria"][0]["port"] = str(flow["selector"]["criteria"][0]["port"]), int(flow["treatment"]["instructions"][0]["port"])
    flow["selector"]["criteria"][1]["mac"], flow["selector"]["criteria"][2]["mac"] = flow["selector"]["criteria"][2]["mac"], flow["selector"]["criteria"][1]["mac"]
    #flow["selector"]["criteria"][3]["ip"], flow["selector"]["criteria"][4]["ip"] = flow["selector"]["criteria"][4]["ip"], flow["selector"]["criteria"][3]["ip"]
    return flow

def make_flows(points, hosts, links):
    flows = []
    dst = f"of:000000000000000{hex(points[len(points) - 1])[2:]}"
    src = f"of:000000000000000{hex(points[0])[2:]}"
    print(dst, src)
    ETH_DST = hosts[dst]["mac"]
    #IP_DST = hosts[dst]["ip"]
    IP_DST = "192.168.0.0/24"
    ETH_SRC = hosts[src]["mac"]
    #IP_SRC = hosts[src]["ip"]
    IP_SRC = "192.168.0.0/24"
    for p in range(0, len(points)):
        OUT_PORT = ""
        IN_PORT = 0
        deviceId = f"of:000000000000000{hex(points[p])[2:]}"
        for link in links:
            if p == 0:
                IN_PORT = 1
                if link["src"]["device"] == deviceId and link["dst"]["device"] == f"of:000000000000000{hex(points[p + 1])[2:]}":
                    OUT_PORT = link["src"]["port"]
            elif p == len(points) - 1:
                OUT_PORT = "1"
                if link["dst"]["device"] == deviceId and link["src"]["device"] == f"of:000000000000000{hex(points[p - 1])[2:]}":
                    IN_PORT = int(link["dst"]["port"])
            else:
                if link["src"]["device"] == deviceId and link["dst"]["device"] == f"of:000000000000000{hex(points[p + 1])[2:]}":
                    OUT_PORT = link["src"]["port"]
                if link["dst"]["device"] == deviceId and link["src"]["device"] == f"of:000000000000000{hex(points[p - 1])[2:]}":
                    IN_PORT = int(link["dst"]["port"])

        flow = {
            "appId": "org.onosproject.fwd",
            "priority": 10,
            "timeout": 0,
            "isPermanent": True,
            "deviceId": deviceId,
            "treatment": {
                "instructions": [
                    {
                        "type": "OUTPUT",
                        "port": OUT_PORT
                    }
                ]
            },
            "selector": {
                "criteria": [
                    {
                        "type": "IN_PORT",
                        "port": IN_PORT
                    },
                    {
                        "type": "ETH_DST",
                        "mac": ETH_DST
                    },
                    {
                        "type": "ETH_SRC",
                        "mac": ETH_SRC
                    }
                ]
            }
        }
        flows.append(flow)
        print(flow)
        flows.append(revert_flow(flow))
        print(flow)
    fl = {"flows": flows}
    return fl

def clearFlows():
    res = req.delete(f"http://{IP}:8181/onos/v1/flows/application/org.onosproject.fwd", auth=USER)
    if res.status_code == 204:
        print("flows fwd are deleted")
    else:
        print("can not delete fwd flows")


def fwd_on():
    res = req.post(f"http://{IP}:8181/onos/v1/applications/org.onosproject.fwd/active", auth=USER)
    if res.status_code == 200:
        print("fwd on")
    else:
        print("some problem occured while fwd on")

def fwd_off():
    res = req.delete(f"http://{IP}:8181/onos/v1/applications/org.onosproject.fwd/active", auth=USER)
    if res.status_code == 204:
        print("fwd off")
    else:
        print("some problem occured while fwd off")


if __name__ == '__main__':
    IP = get_ip()

    links = get_links()

    devices = get_devices_list(links)

    nodes = get_nodes(devices)
    print(nodes)

    graph = dijkstra.Graph.create_from_nodes(nodes)

    #################### No weights ######################
    # Common adjacency matrix that tells us about the switches connections
    graph.adj_mat = matrix.get_matrix(links, len(devices))
    ##################### Weights ########################
    # graph.adj_mat = input_data.main()

    graph.print_adj_mat()
    start_node = graph.get_node_by_data("of:0000000000000001")
    print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(start_node)])
    path_list = graph.dijkstra(start_node)

    #####################################################################

    host_pair = HostPair("h1", "h6")
    points = get_points(path_list)
    print(points.list)

    intents = {"intents": make_intent(points, links, False)}
    points.list.reverse()
    intents["intents"].extend(make_intent(points, links, True))
    data = intents
    # hosts_list = get_hosts()
    # h = hosts(hosts_list)
    # print(h)
    # data = make_flows([1, 4, 3, 6], h, links)

    print("\n")
    print(json.dumps(data, indent=4))

    #deleteIntents.clear()
    #post_flows(data)
    post_intents(intents)

    while True:
        src, dst, w = map(int, input("Input src, dst, w:\n").split())
        if graph.set_new_weight(src, dst, w):
            path_list = graph.dijkstra(start_node)
            print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(start_node)])

            points = get_points(path_list)
            print(points.list)

            intents = {"intents": make_intent(points, links, False)}
            points.list.reverse()
            intents["intents"].extend(make_intent(points, links, True))

            deleteIntents.clear()
            post_intents(intents)

            #fwd_off()
            # clearFlows()
            #
            # data = make_flows(points.list, h, links)
            # post_flows(data)
            #fwd_on()


