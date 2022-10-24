def read_traffic_types():
    res = []
    with open("traffic_types.txt", "r") as f:
        for line in f.readlines():
            splited_line = line.strip("\n").split(";")
            protocol = splited_line[0]
            pairs = [x.strip().split(",") for x in splited_line[1:]]
            res.append([protocol, pairs])
    print(res)
    return res

def get_host_map(nodes):
    m = {}
    for node in nodes:
        if 'ip' in nodes[node]:
            m[node[1:]] = nodes[node]['ip']
    print(m)
    return m

def make_skript(traffic, h_map):
    for t in traffic:
        for n in t[1]:
            print(f'from {h_map[n[0]]} to {h_map[n[1]]}')
        print()

nodes = {'h1': {'ip': '192.168.0.1'}, 's1': {'isSwitch': True}, 'h2': {'ip': '192.168.0.2'}, 's2': {'isSwitch': True},
     'h3': {'ip': '192.168.0.3'}, 's3': {'isSwitch': True}, 'h4': {'ip': '192.168.0.4'}, 's4': {'isSwitch': True},
     'h5': {'ip': '192.168.0.5'}, 's5': {'isSwitch': True}, 'h6': {'ip': '192.168.0.6'}, 's6': {'isSwitch': True}}

tt = read_traffic_types()
host_map = get_host_map(nodes)
make_skript(tt, host_map)
