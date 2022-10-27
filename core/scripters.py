import os

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
                f.writelines(f"-a {h_map[h[1]]} -C 1000 -c 500 -T {t[0]}\n")
            os.chmod(rf"{scripts_path}script{h[0]}", 0o777)


def generate_all_to_all(h_map, rate=1000, pkt_size=512, protocol='UDP'):
    os.system(f'cd {scripts_path} && rm script* -f')
    for k in h_map.keys():
        with open(f"{scripts_path}script{k}", "w") as f:
            for addr in h_map.values():
                if h_map[k] == addr:
                    continue
                f.writelines(f"-a {addr} -C {rate} -c {pkt_size} -T {protocol}\n")
        os.chmod(rf"{scripts_path}script{k}", 0o777)
