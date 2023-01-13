import requests as req
import json

USER = ("onos", "rocks")


def get_intents():
    res = req.get(f"http://172.17.0.2:8181/onos/v1/intents?detail=true", auth=USER)
    intents = res.json()["intents"]
    with open("../jsonFiles/intents.json", "w") as f:
        f.write(json.dumps(res.json(), indent=4))
    return intents


if __name__ == '__main__':
    intents = get_intents()
    SOURCE = "C2:35:2E:08:99:F1"
    DESTINATION = "9E:F0:6D:81:02:48"
    intents_num = 0
    for intent in intents:
        src_mac = intent["treatment"]["instructions"][0]["mac"]
        dst_mac = intent["selector"]["criteria"][0]["mac"]
        if src_mac == SOURCE and dst_mac == DESTINATION or src_mac == DESTINATION and dst_mac == SOURCE:
            intents_num += 1
            print(f'{intent}\n')
    print(f'всего интентов: {intents_num}')