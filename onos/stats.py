import os

import requests as req
import sys
import requests.exceptions
import main
from urllib import parse

USER = ("onos", "rocks")


def get_stats(spm: {}):
    devices_number = 10
    matrix = [[0] * 10 for _ in range(10)]
    try:
        IP = main.get_ip()
        for device in spm:
            for port in spm[device]:
                res = req.get(f"http://{IP}:8181/onos/v1/statistics/flows/link?device={device}&port={port}", auth=USER)
                bytes = res.json()["loads"][0]["latest"]
                if res.json()["loads"][0]["latest"] == -1:
                    bytes = res.json()["loads"][1]["latest"]
                second_device_link = res.json()["loads"][1]["link"]
                all_instances = parse.urlparse(second_device_link)
                dict_from_query = parse.parse_qs(all_instances.query)
                second_device = dict_from_query['device'][0]
                update_matrix(matrix, device, second_device, bytes)
        return matrix
    except requests.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")
        sys.exit()


def get_start_matrix(spm):
    matrix = [[0] * 10 for _ in range(10)]
    for device in spm:
        for port in spm[device]:
            res = req.get(f"http://172.17.0.2:8181/onos/v1/statistics/flows/link?device={device}&port={port}",
                          auth=USER)
            bytes = res.json()["loads"][0]["latest"]
            second_device_link = res.json()["loads"][1]["link"]
            all_instances = parse.urlparse(second_device_link)
            dict_from_query = parse.parse_qs(all_instances.query)
            second_device = dict_from_query['device'][0]
            dev1 = int(device[-1], 16) - 1
            dev2 = int(second_device[-1], 16) - 1
            matrix[dev1][dev2] = round(bytes / 125_000, 2)
            matrix[dev2][dev1] = matrix[dev1][dev2]
    return matrix


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


def read_weights_matrix():
    os.system('cp /home/andre/PycharmProjects/onos_short_path/onos/weights.txt /home/andre/PycharmProjects/onos_short_path/onos/weights_copy.txt')
    with open("/home/andre/PycharmProjects/onos_short_path/onos/weights_copy.txt", "r") as f:
        file = f.readlines()
    weights_matrix = []
    for line in file:
        line = line.strip(', \n')
        weights_matrix.append([float(x) for x in line.split(',')])
    return weights_matrix

if __name__ == '__main__':
    read_weights_matrix()
    # global IP
    # links = main.get_links()
    # src_ports_map = get_spm(links)
    # matrix = get_stats(src_ports_map)
    #
    # all_link_sum = 0
    # print("Передано (Mbit) по каждому каналу за все время моделирования (60 сек.)")
    # for i in range(len(matrix)):
    #     for j in range(len(matrix[i])):
    #         if i < j:
    #             all_link_sum += matrix[i][j]
    #         print('%7.2f' % matrix[i][j], end=', ')
    #     print()
    # print()
    #
    # print("Передавалось (Mbit) в среднем по каждому каналу за 1 сек.)")
    # for i in range(len(matrix)):
    #     for j in range(len(matrix[i])):
    #         print('%7.2f' % (matrix[i][j] / 60), end=', ')
    #     print()
    # print()
    #
    # print("Задействовано из полосы пропускания канала (1 Gbit) в %")
    # for i in range(len(matrix)):
    #     for j in range(len(matrix[i])):
    #         print('%7.2f' % (matrix[i][j] / 60 * 100 / 1000), end=', ')
    #     print()
    # print()
    # print("Свободно полосы пропускания канала (1 Gbit) в %")
    # for i in range(len(matrix)):
    #     for j in range(len(matrix[i])):
    #         print('%7.2f' % (100 - (matrix[i][j] / 60 * 100 / 1000)), end=', ')
    #     print()
    #
    # print(f'Передано всего за время моделирования: {all_link_sum} Mbit')