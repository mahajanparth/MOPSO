from pythonwifi.iwlibs import Wireless
import os
import time
import sys
import socket
import json

wlan0= sys.argv[1]
eth0= sys.argv[2]
print(os.listdir('/sys/class/net/'))
os.chdir('/home/uas-dtu/')
local_ip="127.0.0.1"
local_server_port=20000
local_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
wifi = Wireless('wlan0')
temp_dt = {}
temp_dt["MESSAGE"] = "ADHOC"
temp_dt["SYS_ID"] = 0
temp_dt["PAYLOAD"] = wifi.getMode()
temp_dt["PACKET_NO"] = 0
temp_dt["TIMESTAMP"] = 0
app_json = json.dumps(temp_dt).encode("UTF-8")
local_sock.sendto(app_json, (local_ip,local_server_port))
required_mode="Ad-Hoc"
previous_mode="Ad-Hoc"

mac_addr ="00:00:00:00:00:00"
while True:
    mac_addr=wifi.getAPaddr()
    print("MAC_ADDR",mac_addr)
    if mac_addr !="00:00:00:00:00:00":
        break
    time.sleep(1)

while True:


    time.sleep(1)

    Essid=wifi.getEssid()
    my_mode = wifi.getMode()
    addr=wifi.getAPaddr()

    print("mode is " + str(my_mode),Essid,addr)
    if my_mode != required_mode  or Essid !="swarmmesh" or addr !=mac_addr :
        if addr !="00:00:00:00:00:00":
            mac_addr=addr
        temp_dt = {}
        temp_dt["MESSAGE"] = "ADHOC"
        temp_dt["SYS_ID"] = 0
        temp_dt["PAYLOAD"] = [my_mode,Essid,addr]
        temp_dt["PACKET_NO"] = 0
        temp_dt["TIMESTAMP"] = 0
        app_json = json.dumps(temp_dt).encode("UTF-8")
        local_sock.sendto(app_json, (local_ip, local_server_port))
        time.sleep(3)
        os.system('echo Aether | sudo bash revert_adhoc_jetson.sh')
        os.system('echo Aether | sudo bash revert_adhoc_jetson.sh')

        temp_dt = {}
        temp_dt["MESSAGE"] = "ADHOC"
        temp_dt["SYS_ID"] = 0
        temp_dt["PAYLOAD"] = []
        temp_dt["PACKET_NO"] = 0
        temp_dt["TIMESTAMP"] = 0
        app_json = json.dumps(temp_dt).encode("UTF-8")
        local_sock.sendto(app_json, (local_ip,local_server_port))

        time.sleep(1)
        os.system('echo Aether | sudo bash set_adhoc_jetson.sh '+str(wlan0)+" "+str(eth0))
        os.system('echo Aether | sudo bash set_adhoc_jetson.sh '+str(wlan0)+" "+str(eth0))
        while True:
            mac_addr = wifi.getAPaddr()
            print("MAC_ADDR", mac_addr)
            if mac_addr != "00:00:00:00:00:00":
                break
            time.sleep(1)
        Essid = wifi.getEssid()
        my_mode = wifi.getMode()
        addr = wifi.getAPaddr()

        temp_dt["MESSAGE"] = "ADHOC"
        temp_dt["SYS_ID"] = 0
        temp_dt["PAYLOAD"] = [my_mode,Essid,addr]
        temp_dt["PACKET_NO"] = 0
        temp_dt["TIMESTAMP"] = 0
        app_json = json.dumps(temp_dt).encode("UTF-8")
        local_sock.sendto(app_json, (local_ip, local_server_port))

