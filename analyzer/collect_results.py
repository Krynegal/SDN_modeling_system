#!/usr/bin/python
import json
import os
import sys
from pathlib import Path

itg_path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin'


def decode_all():
    paths = sorted(Path(f'{itg_path}').glob('recv*.log'))
    paths = list(map(str, paths))
    for name in paths:
        new_file = name[0:-4] + "_log.txt"
        os.system(f'cd {itg_path} && ./ITGDec {name} >> {new_file}')
        os.system(f'cd {itg_path} &&  mv {new_file} totalResultsTxt')


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
for file in result_files:
    with open(f"{itg_path}/totalResultsTxt/{file}", "r") as f:
        total_res = False
        splited_rows = []
        for line in f.readlines():
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

with open("all_results.json", "w") as f:
    f.write(json.dumps(all_results, indent=4))
