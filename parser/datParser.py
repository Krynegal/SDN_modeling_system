path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin/'
logs = []
# "Time", "Bitrate", "Delay", "Jitter", "Packet loss"
with open(path + "combined_stats.dat", "r") as f:
    for line in f.readlines():
        split_line = line.split()
        logs.append(split_line[0])
    print(logs)

with open("txtFiles/t.txt", "w") as f:
    for l in logs:
        f.write(l.replace(".", ",")+"\n")