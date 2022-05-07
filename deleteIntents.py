import requests as req
import json

import main

USER = ("onos", "rocks")

def get_intents():
    res = req.get(f"http://{IP}:8181/onos/v1/intents?detail=true", auth=USER)
    intents = res.json()["intents"]
    print(json.dumps(res.json(), indent=4))
    return intents

def delete_all_intents(intents):
    for intent in intents:
        appId = intent["appId"]
        key = intent["key"]
        res = req.delete(f"http://{IP}:8181/onos/v1/intents/{appId}/{key}", auth=USER)
        print(res)

def update_intents(intents):
    for intent in intents:
        if intent["ingressPoint"]["device"] in ["of:0000000000000003", "of:0000000000000006"]:
            appId = intent["appId"]
            key = intent["key"]
            res = req.delete(f"http://{IP}:8181/onos/v1/intents/{appId}/{key}", auth=USER)
            print(res)
    intents = {
        "intents": [{
            "type": "PointToPointIntent",
            "appId": "org.onosproject.cli",
            "priority": 100,
            "ingressPoint": {
                "port": "3",
                "device": "of:0000000000000003"
            },
            "egressPoint": {
                "port": "4",
                "device": "of:0000000000000003"
            }
        }, {
            "type": "PointToPointIntent",
            "appId": "org.onosproject.cli",
            "priority": 100,
            "ingressPoint": {
                "port": "4",
                "device": "of:0000000000000003"
            },
            "egressPoint": {
                "port": "3",
                "device": "of:0000000000000003"
            }
        }, {
            "type": "PointToPointIntent",
            "appId": "org.onosproject.cli",
            "priority": 100,
            "ingressPoint": {
                "port": "3",
                "device": "of:0000000000000005"
            },
            "egressPoint": {
                "port": "5",
                "device": "of:0000000000000005"
            }
        }, {
            "type": "PointToPointIntent",
            "appId": "org.onosproject.cli",
            "priority": 100,
            "ingressPoint": {
                "port": "5",
                "device": "of:0000000000000005"
            },
            "egressPoint": {
                "port": "3",
                "device": "of:0000000000000005"
            }
        }, {
            "type": "PointToPointIntent",
            "appId": "org.onosproject.cli",
            "priority": 100,
            "ingressPoint": {
                "port": "1",
                "device": "of:0000000000000006"
            },
            "egressPoint": {
                "port": "3",
                "device": "of:0000000000000006"
            }
        }, {
            "type": "PointToPointIntent",
            "appId": "org.onosproject.cli",
            "priority": 100,
            "ingressPoint": {
                "port": "3",
                "device": "of:0000000000000006"
            },
            "egressPoint": {
                "port": "1",
                "device": "of:0000000000000006"
            }
        }]
    }
    for intent in intents["intents"]:
        res = req.post(f"http://{IP}:8181/onos/v1/intents", json=intent, auth=USER)
        print(res)

if __name__ == '__main__':
    IP = main.get_ip()
    intents = get_intents()

    update_intents(intents)
    #delete_all_intents(intents)
