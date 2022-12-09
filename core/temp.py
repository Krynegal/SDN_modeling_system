import requests as req
import requests
import sys
from urllib import parse
import json

USER = ("onos", "rocks")

def get_links():
    try:
        IP = '172.17.0.2'
        res = req.get(f"http://{IP}:8181/onos/v1/links", auth=USER)
        links = res.json()["links"]
        with open("../jsonFiles/topology_links.json", "w") as f:
            f.write(json.dumps(res.json(), indent=4))
        print(json.dumps(res.json(), indent=4))
        return links
    except requests.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()

def get_stats(spm: {}):
    devices_number = 10
    matrix = [[0] * devices_number for _ in range(devices_number)]
    try:
        IP = '172.17.0.2'
        for device in spm:
            for port in spm[device]:
                res = req.get(f"http://{IP}:8181/onos/v1/statistics/flows/link?device={device}&port={port}", auth=USER)
                bytes = res.json()["loads"][0]["latest"]
                # "http://172.17.0.2:8181/onos/v1/links?device=of%3A0000000000000002&port=4"
                second_device_link = res.json()["loads"][1]["link"]
                all_instances = parse.urlparse(second_device_link)
                dict_from_query = parse.parse_qs(all_instances.query)
                second_device = dict_from_query['device'][0]
                update_matrix(matrix, device, second_device, bytes)
        return matrix
    except requests.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()


def update_matrix(matrix, dev1, dev2, bytes):
    dev1 = int(dev1[-1], 16) - 1
    dev2 = int(dev2[-1], 16) - 1
    matrix[dev1][dev2] = round(bytes / 125_000, 2)
    matrix[dev2][dev1] = matrix[dev1][dev2]

def get_spm(links):
    src_ports_map = {}
    for link in links:
        if link["dst"]["device"] not in src_ports_map:
            src_ports_map[link["dst"]["device"]] = []
        if (link["src"]["device"] not in src_ports_map) or (
                link["src"]["device"] in src_ports_map and link["src"]["port"] not in src_ports_map[
            link["src"]["device"]]):
            src_ports_map[link["dst"]["device"]].extend(link["dst"]["port"])
    for k in src_ports_map:
        print(f'{k}: {src_ports_map[k]}')
    return src_ports_map