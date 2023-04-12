import os
import random
import time
import datetime

core_path = '/home/andre/PycharmProjects/onos_short_path/core/'
actions_path = core_path + 'actions/'
scripts_path = core_path + 'scripts/'
custom_t_file_path = core_path + 'custom_traffic.txt'


def read_custom_traffic(file_path):
    res = []
    with open(f"{file_path}", "r") as f:
        for line in f.readlines():
            split_line = line.strip("\n").split(";")
            protocol = split_line[0]
            pairs = [x.strip().split(",") for x in split_line[1:]]
            res.append([protocol, pairs])
    print(res)
    return res


def generate_custom(id, h_map, traffic, traffic_conf):
    # os.system(f'cd {scripts_path} && rm script* -f')
    if not os.path.exists(f'{actions_path}action{id}'):
        os.mkdir(f'{actions_path}action{id}')
    for t in traffic:
        for h in t[1]:
            with open(f"{actions_path}action{id}/script{h[0]}", "a") as f:
                if t[0] in ["TCP", "UDP"]:
                    rec_port = random.randint(8999, 11000)
                    duration = int(traffic_conf["duration"]) * 1000  # conversion to milliseconds
                    rate = int(traffic_conf["rate"])
                    pkt_size = int(traffic_conf["pktSize"])
                    f.writelines(f"-a {h_map[h[1]]} -rp {rec_port} -C {rate} -c {pkt_size} -t {duration} -T {t[0]}\n")
                else:
                    f.writelines(f"-a {h_map[h[1]]} {t[0]}\n")
            os.chmod(rf"{actions_path}action{id}/script{h[0]}", 0o777)


def get_pkt_size():
    random.seed(datetime.datetime.now())
    rand_num = random.randint(0, 100) / 100
    if rand_num < 1.6:
        return 1515, 2000
    elif rand_num < 4.9:
        return 256, 511
    elif rand_num < 8.5:
        return 512, 1023
    elif rand_num < 13.9:
        return 128, 255
    elif rand_num < 31.7:
        return 1514, 1514
    elif rand_num < 65.1:
        return 64, 127
    elif rand_num < 100:
        return 1024, 1513


def generate_custom1(id, h_map, traffic, traffic_conf):
    # os.system(f'cd {scripts_path} && rm script* -f')
    if not os.path.exists(f'{actions_path}action{id}'):
        os.mkdir(f'{actions_path}action{id}')
    for t in traffic:
        for h in t[1]:
            with open(f"{actions_path}action{id}/script{h[0]}", "a") as f:
                if t[0] in ["TCP", "UDP"]:
                    rec_port = random.randint(8999, 11000)
                    duration = int(traffic_conf["duration"]) * 1000  # conversion to milliseconds
                    rate = int(traffic_conf["rate"])
                    pkt_size_min, pkt_size_max = get_pkt_size()
                    f.writelines(f"-a {h_map[h[1]]} -rp {rec_port} -C {rate} -u {pkt_size_min} {pkt_size_max} -t {duration} -T {t[0]}\n")
                else:
                    f.writelines(f"-a {h_map[h[1]]} {t[0]}\n")
            os.chmod(rf"{actions_path}action{id}/script{h[0]}", 0o777)


def generate_all_to_all(h_map, rate=1000, pkt_size=512, time=10, protocol='UDP'):
    os.system(f'cd {scripts_path} && rm script* -f')
    for k in h_map.keys():
        with open(f"{scripts_path}script{k}", "w") as f:
            for addr in h_map.values():
                if h_map[k] == addr:
                    continue
                rec_port = random.randint(8999, 11000)
                # -rp {rec_port}
                f.writelines(f"-a {addr} -rp {rec_port} -C {rate} -c {pkt_size} -t {int(time)*1000} -T {protocol}\n")
        os.chmod(rf"{scripts_path}script{k}", 0o777)
