import requests as req
import json
import sys

IP = "172.17.0.5"
USER = ("onos", "rocks")


def get_links():
    try:
        res = req.get(f"http://{IP}:8181/onos/v1/links", auth=USER)
        links = res.json()["links"]
        with open("../jsonFiles/topology_links.json", "w") as f:
            f.write(json.dumps(res.json(), indent=4))
        # print(json.dumps(res.json(), indent=4))
        return links
    except req.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()


def get_hosts():
    try:
        res = req.get(f"http://{IP}:8181/onos/v1/hosts", auth=USER)
        hosts = res.json()["hosts"]
        with open("../jsonFiles/topology_hosts.json", "w") as f:
            f.write(json.dumps(res.json(), indent=4))
        # print(json.dumps(res.json(), indent=4))
        return hosts
    except req.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()


def post_intents(data):
    intents_num = len(data["intents"])
    successful_requests = 0
    for intent in data["intents"]:
        res = req.post(f"http://{IP}:8181/onos/v1/intents", json=intent, auth=USER)
        if res.status_code == 201:
            successful_requests += 1
        else:
            print("NOT SUCCESSFUL REQUEST")
            print(intent)
    if successful_requests != intents_num:
        print(f"Oops. Only {successful_requests}/{intents_num} were successfully sent")
        return
    print(f"{successful_requests}/{intents_num} were successfully send")


def fwd_activate(activate: bool):
    if activate:
        res = req.post(f"http://{IP}:8181/onos/v1/applications/org.onosproject.fwd/active", auth=USER)
        if res.status_code == 200:
            print('fwd is on')
    else:
        res = req.delete(f"http://{IP}:8181/onos/v1/applications/org.onosproject.fwd/active", auth=USER)
        if res.status_code == 204:
            print('fwd is off')
