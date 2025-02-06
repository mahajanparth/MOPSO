#!/bin/bash

echo 'Aether' | sudo -S killall -9 mavproxy.py
sudo killall -9 python3
python3 get_sysid.py
ip=$?
sysid=$(($ip -100))
sudo python3 /home/uas-dtu/Desktop/new_on_uav/emergency_landing.py 500000 $sysid

