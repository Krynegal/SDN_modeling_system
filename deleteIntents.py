import requests as req
import json

USER = ("onos", "rocks")
IP = "192.168.0.114"

def get_intents():
    res = req.get(f"http://{IP}:8181/onos/v1/intents", auth=USER)
    intents = res.json()["intents"]
    print(json.dumps(res.json(), indent=4))
    return intents

def delete_all_intents(intents):
    for intent in intents:
        appId = intent["appId"]
        key = intent["key"]
        res = req.delete(f"http://{IP}:8181/onos/v1/intents/{appId}/{key}", auth=USER)
        print(res)

if __name__ == '__main__':
    #intents = get_intents()
    #delete_all_intents(intents)
    get_ip()