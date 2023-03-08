#!/usr/bin/python
import json
import statistics
from numpy import percentile

duration = 60


def pprint(data):
    print(f"mean: {statistics.mean(data)}")
    print(f"mode: {statistics.mode(data)}")
    print(f"median: {statistics.median(data)}")
    print(f"percentile: {percentile(data, 90)}")
    print(f"standard deviation: {statistics.pstdev(data)}")
    print(f"dispersion: {statistics.pvariance(data)}")
    print()


with open("all_results.json", "r") as f:
    all_results = json.loads(f.read())

total_pkts_recv = [int(all_results[i]["Total packets"]) for i in all_results]
dropped_pkts = [int(all_results[i]["Packets dropped"]) for i in all_results]
packet_loss_for_each_receiver = []
for i in range(len(total_pkts_recv)):
    if total_pkts_recv[i] + dropped_pkts[i] == 0:
        print(all_results[str(i)])
    else:
        packet_loss_for_each_receiver.append(round((dropped_pkts[i] / (total_pkts_recv[i] + dropped_pkts[i]))*100, 2))
print(f"packet loss for each receiver: {packet_loss_for_each_receiver}")
print(f"total packet loss: {round((sum(dropped_pkts) / (sum(total_pkts_recv) + sum(dropped_pkts)))*100, 2)} %\n")
t = []
for i in range(len(total_pkts_recv)):
    t.append(total_pkts_recv[i] + dropped_pkts[i])
print(f'dropped + received: {t}')
packet_rate = [x / duration for x in t]
print(f'mean packet rate: {round(statistics.mean(packet_rate), 2)}')
print(f'median packet rate: {round(statistics.median(packet_rate), 2)}')
pprint(packet_loss_for_each_receiver)

delays = [float(all_results[i]["Average delay"]) * 1000 for i in all_results]  # delays in ms
print(delays)
pprint(delays)

jitters = [float(all_results[i]["Average jitter"]) * 1000 for i in all_results]  # jitter in ms
print(jitters)
pprint(jitters)
