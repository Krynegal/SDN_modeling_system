import yaml


def get_yaml_content():
    with open('/home/andre/PycharmProjects/onos_short_path/core/scenario.yaml') as f:
        scenario = yaml.load(f, Loader=yaml.Loader)
    return scenario


def find_max_flow_duration(scenario):
    max_dur = 0
    for flow in scenario["flows"]:
        max_dur = max(flow["traffic_conf"]["duration"], max_dur)
    return max_dur


if __name__ == '__main__':
    scenario = get_yaml_content()
    print(find_max_flow_duration(scenario))
    print(scenario)
