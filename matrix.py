import json

with open("topology_links.json", "r") as f:
    links = json.loads(f.read())["links"]
#print(json.dumps(links, indent=4))

devices = []
for link in links:
    devices.append(link["src"]["device"])
devices = list(set(devices))


def print_matrix(matrix):
    for row in matrix:
        print(row)


def get_matrix(links, devices_num):
    matrix = [[0] * devices_num for _ in range(devices_num)]
    for link in links:
        src = int(link["src"]["device"][-1])
        dst = int(link["dst"]["device"][-1])
        matrix[dst - 1][src - 1] = 1
    return matrix
