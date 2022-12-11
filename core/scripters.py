import os
import random

core_path = '/home/andre/PycharmProjects/onos_short_path/core/'
scripts_path = core_path + 'scripts/'
custom_t_file_path = core_path + 'custom_traffic.txt'


def read_custom_traffic():
    res = []
    with open(f"{custom_t_file_path}", "r") as f:
        for line in f.readlines():
            split_line = line.strip("\n").split(";")
            protocol = split_line[0]
            pairs = [x.strip().split(",") for x in split_line[1:]]
            res.append([protocol, pairs])
    print(res)
    return res


def generate_custom(h_map, traffic):
    os.system(f'cd {scripts_path} && rm script* -f')
    for t in traffic:
        for h in t[1]:
            with open(f"{scripts_path}script{h[0]}", "a") as f:
                if t[0] in ["TCP", "UDP"]:
                    rec_port = random.randint(8999, 11000)
                    #-rp {rec_port}
                    f.writelines(f"-a {h_map[h[1]]} -rp {rec_port} -C 10000 -c 1000 -t 60000 -T {t[0]}\n")
                else:
                    f.writelines(f"-a {h_map[h[1]]} {t[0]}\n")
            os.chmod(rf"{scripts_path}script{h[0]}", 0o777)


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
