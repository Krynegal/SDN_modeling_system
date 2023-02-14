import yaml


def get_yaml_content():
    with open('/home/andre/PycharmProjects/onos_short_path/core/scenario.yaml') as f:
        read_data = yaml.load(f, Loader=yaml.Loader)
    return read_data


def find_max_flow_duration(read_data):
    max_dur = 0
    for s in read_data["scenario"]:
        max_dur = max(s["script"]["traffic_conf"]["duration"], max_dur)
    return max_dur


if __name__ == '__main__':
    res = get_yaml_content()
    print(res)
