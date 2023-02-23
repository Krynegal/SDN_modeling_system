import sys

import requests as req

import requests.exceptions

import main
IP = "172.17.0.5"
USER = ("onos", "rocks")


def get_intents():
    try:
        res = req.get(f"http://{IP}:8181/onos/v1/intents?detail=true", auth=USER)
        intents = res.json()["intents"]
        # print(json.dumps(res.json(), indent=4))
        return intents
    except requests.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()


def delete_all_intents(intents):
    successful_requests = 0
    intents_num = len(intents)
    for intent in intents:
        appId, key = intent["appId"], intent["key"]
        res = req.delete(f"http://{IP}:8181/onos/v1/intents/{appId}/{key}", auth=USER)
        if res.status_code == 204:
            successful_requests += 1
    if successful_requests == intents_num:
        print(f"{successful_requests}/{intents_num} were successfully deleted")
    else:
        print(f"Oops. Only {successful_requests}/{intents_num} were successfully deleted")
        clear()


def clear():
    intents = get_intents()
    delete_all_intents(intents)


if __name__ == '__main__':
    clear()
