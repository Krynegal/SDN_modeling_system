import yaml

with open('../configs/configs.yaml', 'r') as f:
    cfg = yaml.load(f, Loader=yaml.Loader)

core_path = cfg["core_path"]
onos_path = cfg["onos_path"]
itg_path = cfg["itg_path"]
VM = cfg["VM"]
IP = cfg["IP"]
used_onos_controllers = cfg["used_onos_controllers"]
