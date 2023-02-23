import os

import requests as req
import sys
from urllib import parse
import numpy as np

IP = "172.17.0.5"
USER = ("onos", "rocks")


def get_stats(matrix, spm: {}):
    try:
        for device in spm:
            for port in spm[device]:
                res = req.get(f"http://{IP}:8181/onos/v1/statistics/flows/link?device={device}&port={port}", auth=USER)
                # print(device, port)
                bytes = 0
                if len(res.json()["loads"]) > 0:
                    bytes += res.json()["loads"][0]["rate"]
                else:
                    print(f'res.json()["loads"] is empty')
                    print(f'device: {device}, port: {port}')
                    print()
                if len(res.json()["loads"]) > 1:
                    bytes += res.json()["loads"][1]["rate"]

                    second_device_link = res.json()["loads"][1]["link"]
                    all_instances = parse.urlparse(second_device_link)
                    dict_from_query = parse.parse_qs(all_instances.query)
                    second_device = dict_from_query['device'][0]
                    update_matrix(matrix, device, second_device, bytes)
        return matrix
    except req.exceptions.ConnectionError:
        print("Oops. Seems like dns lookup failed..")


def update_matrix(matrix, dev1, dev2, bytes):
    dev1 = int(dev1[3:], 16) - 1
    dev2 = int(dev2[3:], 16) - 1
    # Переводим байты в мегабайты
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
    print('src_ports_map:')
    for k in src_ports_map:
        print(f'{k}: {src_ports_map[k]}')
    return src_ports_map


def read_weights_matrix():
    os.system('cp /home/andre/PycharmProjects/onos_short_path/onos/weights.txt '
              '/home/andre/PycharmProjects/onos_short_path/onos/taken_weights.txt')
    with open("/home/andre/PycharmProjects/onos_short_path/onos/taken_weights.txt", "r") as f:
        file = f.readlines()
    weights_matrix = []
    for line in file:
        if line == '\n':
            break
        line = line.strip(', \n')
        weights_matrix.append([float(x) for x in line.split(',')])
    return weights_matrix


if __name__ == '__main__':
    # read_weights_matrix()
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
    print(hex(10)[2:])
