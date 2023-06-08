#!/usr/bin/python
import json
import sys
import statistics
from numpy import percentile

args = sys.argv
if len(args) != 2:
    print("arguments are required: duration=...")
    sys.exit()
duration = int(args[1])



def pprint(metric, data):
    print(f"{metric}: ")
    print(f"\tmean: {statistics.mean(data)}")
    print(f"\tmode: {statistics.mode(data)}")
    print(f"\tmedian: {statistics.median(data)}")
    print(f"\t90 percentile: {percentile(data, 90)}")
    print(f"\tstandard deviation: {statistics.pstdev(data)}")
    print(f"\tdispersion: {statistics.pvariance(data)}")
    print()


with open("all_results.json", "r") as f:
    all_results = json.loads(f.read())

total_pkts_recv = [int(all_results[i]["Total packets"]) for i in all_results]
dropped_pkts = [int(all_results[i]["Packets dropped"]) for i in all_results]
received_bytes = [int(all_results[i]["Bytes received"]) for i in all_results]

packet_loss_for_each_receiver = []
for i in range(len(total_pkts_recv)):
    if total_pkts_recv[i] + dropped_pkts[i] == 0:
        print(all_results[str(i)])
    else:
        packet_loss_for_each_receiver.append(round((dropped_pkts[i] / (total_pkts_recv[i] + dropped_pkts[i])) * 100, 2))

print(f'received: {total_pkts_recv}')
print(f'dropped: {dropped_pkts}\n')
print(f"packet loss for each receiver: {packet_loss_for_each_receiver}")
print(f"total packet loss: {round((sum(dropped_pkts) / (sum(total_pkts_recv) + sum(dropped_pkts))) * 100, 2)} %\n")
pprint("packet loss", packet_loss_for_each_receiver)

#print(f"throughput: {round(sum(total_pkts_recv) / duration * pkt_size / 125_000, 2)} Mbts/s \n")
print(f"throughput: {round(sum(received_bytes) / duration / 125_000, 2)} Mbts/s \n")

t = []
for i in range(len(total_pkts_recv)):
    t.append(total_pkts_recv[i] + dropped_pkts[i])
packet_rate = [x / duration for x in t]
print("packet rate:")
print(f'\tmean packet rate: {round(statistics.mean(packet_rate), 2)}')
print(f'\tmedian packet rate: {round(statistics.median(packet_rate), 2)}\n')

delays = [float(all_results[i]["Average delay"]) * 1000 for i in all_results]  # delays in ms
print(delays)
pprint("delay", delays)

jitters = [float(all_results[i]["Average jitter"]) * 1000 for i in all_results]  # jitter in ms
print(jitters)
pprint("jitter", jitters)
