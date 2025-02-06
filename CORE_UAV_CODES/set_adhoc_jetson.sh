#!/bin/bash

#sets the jetson nano in ac-hoc mode

#put your settings here...
adapter_external="wlan0"
multicast_interface="eth0"
network_name="swarmmesh"
cell_id=7E:59:40:C3:76:46  	#comment out to randomly assign cell id
network_key=1234567890
network_channel=3
host_id=$1
host_id2=$2
tx_power=2000

sudo systemctl stop NetworkManager
sudo systemctl disable NetworkManager
sudo systemctl mask NetworkManager

echo "Setting the external Wi-Fi adapter in ad-hoc mode..."
adapter_to_use=$adapter_external
sudo ip link set $adapter_to_use down

sudo iwconfig $adapter_to_use mode ad-hoc
sudo iwconfig $adapter_to_use channel $network_channel
sudo iwconfig $adapter_to_use essid $network_name
if [ $cell_id ]; then
	echo "Setting hard coded cell id..."
	sudo iwconfig $adapter_to_use ap $cell_id
else
    echo "Setting random cell id..."
    sudo iwconfig $adapter_to_use ap any
fi
sudo iwconfig $adapter_to_use key $network_key

sudo ip link set $adapter_to_use up

sudo ip addr add 192.168.4.$host_id/24 dev $adapter_to_use
sudo iw dev $adapter_to_use set txpower fixed $tx_power

sudo ip link set $multicast_interface up
sudo ip addr add 192.168.0.$host_id2/24 dev $multicast_interface

sudo route add -net 224.0.0.0 netmask 255.255.255.0 $adapter_external
sudo route add -net 239.0.0.0 netmask 255.255.255.0 $multicast_interface

echo "Wi-Fi adapter set into ad-hoc mode."
