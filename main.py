import requests as req
import json
import dijkstra
import matrix

USER = ("onos", "rocks")
IP = "192.168.1.91"

res = req.get(f"http://{IP}:8181/onos/v1/links", auth=USER)
links = res.json()
with open("topology_links.json", "w") as f:
   f.write(json.dumps(res.json(), indent=4))
#print(json.dumps(res.json(), indent=4))


class Path:
    def __init__(self, *args):
        self.list = [x for x in args]


class HostPair:
    def __init__(self, h1, h2):
        self.h1 = h1
        self.h2 = h2


host_pair = HostPair("h1", "h6")


####################### Использование весов #########################
a = dijkstra.Node("sw1")
b = dijkstra.Node("sw2")
c = dijkstra.Node("sw3")
d = dijkstra.Node("sw4")
e = dijkstra.Node("sw5")
f = dijkstra.Node("sw6")

graph = dijkstra.Graph.create_from_nodes([a, b, c, d, e, f])
graph.connect(a, b, 5)
graph.connect(a, c, 10)
graph.connect(a, e, 2)
graph.connect(b, c, 2)
graph.connect(b, d, 4)
graph.connect(c, d, 7)
graph.connect(c, f, 10)
graph.connect(d, e, 3)

graph.print_adj_mat()
print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(a)])
path_list = graph.dijkstra(a)



############################# Без весов #############################
# devices = []
# for device in matrix.devices:
#     devices.append(device[-1])
# devices.sort()
# nodes = []
# for device_num in devices:
#     nodes.append(dijkstra.Node("sw" + device_num))
#
# graph = dijkstra.Graph.create_from_nodes(nodes)
# graph.adj_mat = dijkstra.matrix.get_matrix(dijkstra.matrix.links, len(dijkstra.matrix.devices))
# graph.print_adj_mat()
# n = graph.get_node_by_data("sw1")
# print([(weight, [n.data for n in node]) for (weight, node) in graph.dijkstra(n)])
# path_list = graph.dijkstra(n)


for list in path_list:
    nodes = list[1]
    if nodes[-1].data[-1] == host_pair.h2[-1]:
        num_nodes = [int(_.data[-1]) for _ in nodes]
        points = Path()
        points.list = num_nodes
        print()


#points = Path(1, 2, 4, 3, 5, 6)
#print(points.list)


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
        for link in links["links"]:
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


intents = {"intents": []}
intents["intents"] = make_intent(points, links)

points.list.reverse()
intents["intents"].extend(make_intent(points, links))
data = intents
print("\n")
print(json.dumps(data, indent=4))

for intent in data["intents"]:
    res = req.post(f"http://{IP}:8181/onos/v1/intents", json=intent, auth=USER)
    print(res)
