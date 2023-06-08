#!/usr/bin/python
import json
import os
import sys
from pathlib import Path

itg_path = '/home/andrey/D-ITG-2.8.1-r1023/bin'


def decode_all():
    paths = sorted(Path(f'{itg_path}').glob('recv*.log'))
    paths = list(map(str, paths))
    for name in paths:
        new_file = name[0:-4] + "_log.txt"
        os.system(f'cd {itg_path} && ./ITGDec {name} >> {new_file}')
        os.system(f'cd {itg_path} &&  mv {new_file} totalResultsTxt')
        #  os.system(f'cd {itg_path} && rm -f {name}')

def get_file_num(name: str):
    res = ""
    for c in name:
        if c.isdigit():
            res += c
    return int(res)


os.system(f'cd {itg_path} && mkdir -p totalResultsTxt')
os.system(f'cd {itg_path} && rm -rf totalResultsTxt/*')

decode_all()
result_files = os.listdir(f"{itg_path}/totalResultsTxt")
all_results = {}
print(result_files)
all_losses = {}
for file in result_files:
    with open(f"{itg_path}/totalResultsTxt/{file}", "r") as f:
        lossesStart = False
        total_res = False
        splited_rows = []
        losses = []
        for line in f.readlines():
            if line.strip() == "LossesStop":
                lossesStart = False
            if lossesStart:
                losses.append([int(x.strip()) for x in line.strip().split(" ")])
            if line.strip() == "LossesStart":
                lossesStart = True
            if line.strip() == "****************  TOTAL RESULTS   ******************":
                total_res = True
            if total_res:
                splited_row = [x.strip() for x in line.strip().split("=")]
                print(splited_row)
                splited_rows.append(splited_row)
    splited_rows = splited_rows[2:len(splited_rows)-2]
    print()
    t = {
        'Number of flows': '',
        'Total time': '',
        'Total packets': '',
        'Minimum delay': '',
        'Maximum delay': '',
        'Average delay': '',
        'Average jitter': '',
        'Delay standard deviation': '',
        'Bytes received': '',
        'Average bitrate': '',
        'Average packet rate': '',
        'Packets dropped': '',
        'Packets dropped percent': '',
        'Average loss-burst size': '',
    }

    for row in splited_rows:
        print(row)
        if "(" in row[1]:
            t[row[0]] = row[1].split(" (")[0]
            percent = row[1].split(" (")[1]
            t["Packets dropped percent"] = percent[:len(percent)-3]
        else:
            t[row[0]] = row[1].split(" ")[0]
    if t["Number of flows"] == "0":
        continue
    all_results[get_file_num(file)] = t
    
    print(f'losses {losses}')
    if len(losses) == 0:
        continue
    prev = losses[-1]
    res = [prev]
    for i in range(len(losses)-2, 0, -1):
        if losses[i][1] < prev[1] and losses[i][0] < prev[0]:
            res.append(losses[i])
            prev = losses[i]
        else:
            continue
    print(res)
    res.sort(key=lambda i: i[1])
    if res[0][1] == 0:
        res = res[1:]
    print(res)
    

    points = []
    prev = 0
    for point in res:
        x = point[0] / 29
        y = point[1] - prev
        r = point[2]
        prev = point[1]
        points.append({"x": x, "y": y, "r": r})
    print(f'points: {points}')

    all_losses[get_file_num(file)] = points

with open("all_results.json", "w") as f:
    f.write(json.dumps(all_results, indent=4))


with open("all_losses.json", "w") as f:
    f.write(json.dumps(all_losses, indent=4))
