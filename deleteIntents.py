import requests as req
import json

USER = ("onos", "rocks")
IP = "192.168.1.91"

res = req.get(f"http://{IP}:8181/onos/v1/intents", auth=USER)
intents = res.json()
print(json.dumps(res.json(), indent=4))


for intent in intents["intents"]:
    appId = intent["appId"]
    key = intent["key"]
    res = req.delete(f"http://{IP}:8181/onos/v1/intents/{appId}/{key}", auth=USER)
    print(res)
