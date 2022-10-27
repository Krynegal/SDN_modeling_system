import time

core_path = '/home/andre/PycharmProjects/onos_short_path/core/'
scripts_path = core_path + 'scripts/'
itg_path = '/home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin'


def run_custom(hosts: [], senders: [], receivers: []):
    print(f'receivers: {receivers}')
    print(f'senders: {senders}')
    print('---start of processing---')
    print('processing...')
    for i in receivers:
        hosts[int(i) - 1].cmd('kill -9 $(pidof ITGRecv)')
    for i in receivers:
        hosts[int(i) - 1].cmd(f'cd {itg_path} && ./ITGRecv -l recv{i}.log &')
    time.sleep(3)

    for i in senders:
        hosts[int(i) - 1].cmd(f'cd {itg_path} && ./ITGSend {scripts_path}script{i} -l send{i}.log &')
    time.sleep(5)
    print('---end of processing---')


def run_all(hosts: []):
    hosts_num = len(hosts)
    print('---start of processing---')
    print('processing...')
    for i in range(1, hosts_num + 1):
        hosts[i - 1].cmd('kill -9 $(pidof ITGRecv)')
    for i in range(1, hosts_num + 1):
        hosts[i - 1].cmd(f'cd {itg_path} && ./ITGRecv -l recv_all_{i}.log &')
    time.sleep(3)

    for i in range(1, hosts_num + 1):
        hosts[i - 1].cmd(f'cd {itg_path} && ./ITGSend {scripts_path}script{i} -l send_all_{i}.log &')
    time.sleep(5)
    print('---end of processing---')
