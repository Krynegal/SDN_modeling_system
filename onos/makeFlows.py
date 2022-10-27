import requests as req
import json
import sys

USER = ("onos", "rocks")

points = [1, 2, 3, 6]

def get_links():
    try:
        res = req.get(f"http://172.17.0.2:8181/onos/v1/links", auth=USER)
        links = res.json()["links"]
        with open("../jsonFiles/topology_links.json", "w") as f:
            f.write(json.dumps(res.json(), indent=4))
        #print(json.dumps(res.json(), indent=4))
        return links
    except req.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()

def get_hosts():
    try:
        res = req.get(f"http://172.17.0.2:8181/onos/v1/hosts", auth=USER)
        hosts = res.json()["hosts"]
        with open("../jsonFiles/topology_hosts.json", "w") as f:
            f.write(json.dumps(res.json(), indent=4))
        #print(json.dumps(res.json(), indent=4))
        return hosts
    except req.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()

def hosts(hosts):
    h = {}
    for host in hosts:
        h[host["locations"][0]["elementId"]] = host["mac"]
    return h

def revert_flow(flow):
    flow["treatment"]["instructions"][0]["port"], flow["selector"]["criteria"][0]["port"] = str(flow["selector"]["criteria"][0]["port"]), int(flow["treatment"]["instructions"][0]["port"])
    flow["selector"]["criteria"][1]["mac"], flow["selector"]["criteria"][2]["mac"] = flow["selector"]["criteria"][2]["mac"], flow["selector"]["criteria"][1]["mac"]
    return flow

def make_flows(points, hosts, links):
    flows = []
    dst = f"of:000000000000000{hex(points[len(points) - 1])[2:]}"
    src = f"of:000000000000000{hex(points[0])[2:]}"
    print(dst, src)
    ETH_DST = hosts[dst]
    #ETH_DST = "7E:65:F9:E7:76:F9"
    ETH_SRC = hosts[src]
    #ETH_SRC = "AE:EE:0A:8F:2B:4A"
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
            "priority": 100,
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
    with open("../jsonFiles/flows_out.json", "w") as f:
        f.write(json.dumps(fl, indent=4))

if __name__ == '__main__':
    links = get_links()
    hosts_list = get_hosts()
    h = hosts(hosts_list)
    print(h)

    make_flows(points, h, links)

