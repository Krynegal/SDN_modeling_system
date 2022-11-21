#!/bin/bash

sudo systemctl start ovs-vswitchd
echo start ovs-vswitch

docker start onos
echo start onos

gnome-terminal -- bash -c "cd /home/andre/PycharmProjects/onos_short_path/core/; exec bash"
gnome-terminal -- bash -c "cd /home/andre/Загрузки/D-ITG-2.8.1-r1023-src/D-ITG-2.8.1-r1023/bin/; exec bash"

cd /home/andre/PycharmProjects/onos_short_path/parser/ && jupyter notebook
echo start jupyter

