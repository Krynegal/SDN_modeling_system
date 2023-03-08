import requests as req
import json
from configs.configs import IP

USER = ("onos", "rocks")


def get_intents():
    res = req.get(f"http://{IP}:8181/onos/v1/intents?detail=true", auth=USER)
    intents = res.json()["intents"]
    with open("../jsonFiles/intents.json", "w") as f:
        f.write(json.dumps(res.json(), indent=4))
    return intents


if __name__ == '__main__':
    intents = get_intents()
    SOURCE = "72:F1:8C:8D:AA:1C"
    DESTINATION = "62:C4:7E:48:4B:E9"
    intents_num = 0
    for intent in intents:
        src_mac = intent["treatment"]["instructions"][0]["mac"]
        dst_mac = intent["selector"]["criteria"][0]["mac"]
        if src_mac == SOURCE and dst_mac == DESTINATION or src_mac == DESTINATION and dst_mac == SOURCE:
            intents_num += 1
            print(f'{intent}\n')
    print(f'всего интентов: {intents_num}')