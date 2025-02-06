#!/bin/bash

#sets the jetson nano in managed (station) mode

#put your settings here...
adapter_external="wlan0"
tx_power=2000

sudo systemctl stop NetworkManager
sudo systemctl disable NetworkManager
sudo systemctl mask NetworkManager
echo "Reverting external Wi-Fi adapter to default settings..."
adapter_to_use=$adapter_external
sudo ip link set $adapter_to_use down

sudo iwconfig $adapter_to_use mode managed

sudo ip link set $adapter_to_use up

sudo iw dev $adapter_to_use set txpower fixed $tx_power

sudo systemctl unmask NetworkManager
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

echo "Wi-Fi adapter reverted to default settings."
