import yaml


def get_yaml_content():
    with open('/home/andre/PycharmProjects/onos_short_path/core/scenario.yaml') as f:
        read_data = yaml.load(f, Loader=yaml.Loader)
    return read_data


if __name__ == '__main__':
    res = get_yaml_content()
    print(res)
