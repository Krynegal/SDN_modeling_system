import yaml
from configs.configs import core_path


def read_scenario():
    with open(f'{core_path}/scenario.yaml') as f:
        scenario = yaml.load(f, Loader=yaml.Loader)
    return scenario


def find_max_flow_duration(scenario):
    max_dur = 0
    for flow in scenario["flows"]:
        max_dur = max(flow["traffic_conf"]["duration"], max_dur)
    return max_dur


if __name__ == '__main__':
    scenario = read_scenario()
    print(find_max_flow_duration(scenario))
    print(scenario)
