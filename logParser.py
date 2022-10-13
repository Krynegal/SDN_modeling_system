path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin/'
logs = []
with open(path + "res4.txt", "r") as f:
    for line in f.readlines():
        split_line = line.split()
        log = {
            "flow": split_line[0][-4:],
            "seq": split_line[2],
            "src": split_line[4],
            "dst": split_line[6],
            "txTime": split_line[7][7:],
            "rxTime": split_line[8][7:],
            "size": split_line[10],
        }
        logs.append(log)
    print(logs)

with open("size.txt", "w") as f:
    for log in logs:
        f.write(log["size"]+"\n")

with open("time.txt", "w") as f:
    for log in logs:
        f.write(log["txTime"]+"\n")
