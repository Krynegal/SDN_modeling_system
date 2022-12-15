#!/usr/bin/python
import os
import sys

traffic = [['1', '2'], ['1', '4'], ['1', '6'], ['1', '8'], ['1', '10'], ['2', '1'], ['2', '3'], ['2', '5'],
                    ['2', '7'], ['2', '9'], ['3', '2'], ['3', '4'], ['3', '6'], ['3', '8'], ['3', '10'], ['4', '1'],
                    ['4', '3'], ['4', '5'], ['4', '7'], ['4', '9'], ['5', '2'], ['5', '4'], ['5', '6'], ['5', '8'],
                    ['5', '10'], ['6', '1'], ['6', '3'], ['6', '5'], ['6', '7'], ['6', '9'], ['7', '2'], ['7', '4'],
                    ['7', '6'], ['7', '8'], ['7', '10'], ['8', '1'], ['8', '3'], ['8', '5'], ['8', '7'], ['8', '9'],
                    ['9', '2'], ['9', '4'], ['9', '6'], ['9', '8'], ['9', '10'], ['10', '1'], ['10', '3'],
                    ['10', '5'], ['10', '7'], ['10', '9']]
#traffic = [['udp', [['1', '2'], ['1', '4'], ['4', '1']]]]

def get_switch_start_pairs(traffic):
    switch_start_pairs = {}
    for pair in traffic:
        src_host = int(pair[0])
        start_switch = int(src_host / 2)
        if src_host % 2 != 0:
            start_switch = int((src_host + 1) / 2)
        if start_switch not in switch_start_pairs:
            switch_start_pairs[start_switch] = []
        switch_start_pairs[start_switch].append(pair)
    return switch_start_pairs

def get_src_dsts_host_map(traffic):
    m = {}
    for pair in traffic:
        src, dst = pair[0], pair[1]
        if src not in m:
            m[src] = []
        if dst in m and src in m[dst]:
            continue
        m[src].append(dst)
    return m


def remove_duplicates(all_traffic):
    without_dup = get_src_dsts_host_map(all_traffic)
    res = []
    for key in without_dup:
        for dst in without_dup[key]:
            res.append([key, dst])
    return res

if __name__ == '__main__':
    print(len(traffic))
    traffic = remove_duplicates(traffic)
    print(len(traffic))
    switch_start_pairs = get_switch_start_pairs(traffic)
    print(switch_start_pairs)
