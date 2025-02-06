import os
import time
import socket
import pickle
import signal
import dronekit
import paramiko
import threading
import matplotlib
import numpy as np
import tkinter as Tk
import netifaces as ni
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from GUI import graphic
from scp import SCPClient
from scipy.spatial import distance
from multiprocessing import Process
from dronekit import connect, VehicleMode

global graphic_object
graphic_object = graphic()

global params
ID = 0
def Set_Ad_hoc_func():
	os.system("sudo service network-manager stop")
	os.system("sudo ip link set wlp3s0 down")
	os.system("sudo iwconfig wlp3s0 mode ad-hoc")
	os.system("sudo iwconfig wlp3s0 channel 3")
	os.system("sudo iwconfig wlp3s0 essid 'swarmmesh'")
	os.system("sudo iwconfig wlp3s0 key 1234567890")
	os.system("sudo ip link set wlp3s0 up")
	os.system("sudo ip addr add 192.168.4.210/24 dev wlp3s0")
	os.system("sudo ip addr add 192.168.1.10/24 dev enp2s0")

def Disable_Ad_hoc_func():
	os.system("sudo service network-manager stop")
	os.system("sudo ip link set wlp3s0 down")
	os.system("sudo iwconfig wlp3s0 mode managed")
	os.system("sudo ip link set wlp3s0 up")
	os.system("sudo service network-manager start")
	os.system("sudo dhclient wlp3s0")
	os.system("sudo dhclient enp2s0")

def Test_connections_func():
	Num_of_UAVs = params[0]
	UAV_list = list(range(211,211+Num_of_UAVs))
	Connection_list = list()

	while (len(UAV_list) != 0):
		for i in UAV_list:
			server_ip = "192.168.4.{0}".format(i)
			result = os.system('ping -c 1 ' + server_ip)

			if result == 0:
				print ("connected to UAV ",(i%10))
				UAV_list.remove(i)
				Connection_list.append(i)
		print (Connection_list)

def Land_func():
	vehicle = list()
	Num_of_UAVs = params[0]

	for i in range(N):
	    vehicle[i] = connect('127.0.0.1:'+str(14550+i))
	    time.sleep(0.5)
	    vehicle[i].mode = VehicleMode("LAND")

def Plan_mission_func():
	ID = threading.get_ident()
	os.chdir("/home/aniket/ardupilot/ArduCopter")
	os.system("sim_vehicle.py -L L1 --map -w")

def Save_wp_func():
	vehicle = connect('127.0.0.1:14550')

	cmds = vehicle.commands
	cmds.download()
	cmds.wait_ready()
	waypoint_list=list()

	for cmd in cmds:
		waypoint_list.append([cmd.x,cmd.y])

	dump_wp_file = open("waypoint_list", "wb")
	pickle.dump(waypoint_list, dump_wp_file)
	dump_wp_file.close()

def Kill_map_func():
	"""
	print("reached here")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(("127.0.0.1",5000))
	data, addr = sock.recvfrom(64)
	pid = list(map(float,data.strip("/n").split(" ")))
	print("reached here2")
	print(pid)
	ck.sendto(str(pid),("127.0.0.1",5000))
	sock.shutdown()
	sock.close()"""
	

def Plan_formation_func():
	weight_matrix = graphic_object.display()
	dump_weight_matrix_file = open("weight_matrix", "wb")
	pickle.dump(weight_matrix, dump_weight_matrix_file)
	dump_weight_matrix_file.close()

def Upload_mission_func():
	Num_of_UAVs = params[0]
	host="192.168.1.41"
	port=50000
	UAV_list = list(range(211,211+Num_of_UAVs))

	def createSSHClient(server, port, user, password):
	    client = paramiko.SSHClient()
	    client.load_system_host_keys()
	    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	    client.connect(server, port, user, password)
	    return client

	for i in uavlist:
		ssh = createSSHClient("192.168.4.{0}".format(i),22,"pi","raspberry")
		scp = SCPClient(ssh.get_transport())
		scp.put('waypoint_list','waypoint_list')
		scp.put('params','params')
		scp.put('weight_matrix','weight_matrix')
		print("Sent to UAV ",(i%10))

def Start_mission_func():
	os.chdir("/home/aniket/IAF/GUI")
	os.system("python start_mission.py")

home_layout = [[sg.Text('Swarm Planner', size=(22, 1), font=("Helvetica", 25), text_color='#033F63',justification='left'), sg.Image("logo_50.png")],
	[sg.Text('='  * 100, size=(80, 1), justification='center')],
	[sg.Text('Enter the Number of UAVs',size=(36,1),justification='right'), sg.InputText()],
	[sg.Text('Enter the UAV_ID that will remain in front',size=(36,1),justification='right'), sg.InputText()],
	[sg.Text('Enter the minimum distance between UAVs',size=(36,1),justification='right'), sg.InputText()],
	[sg.Text('_'  * 100, size=(80, 1), justification='center')],
	[sg.Button('Enable Ad-hoc Mode', button_color=('white', '#033F63')), sg.Button('Disable Ad-hoc Mode', button_color=('white', '#033F63')),sg.Button('Test connections', button_color=('white', '#033F63')), sg.Button('Land All UAVs', button_color=('white', '#EE6C4D'))],
	[sg.Button('Plan Mission', button_color=('white', '#033F63')), sg.Button('Save Waypoints', button_color=('white', '#033F63')), sg.Button('Kill Map', button_color=('white', '#033F63')), sg.Button('Plan Formation', button_color=('white', '#033F63')),  sg.Button('Upload Mission', button_color=('white', '#033F63'))],
	[sg.Text('_'  * 100, size=(80, 1), justification='center')],
	[sg.Button('Start Mission', button_color=('white', 'green'))]]

if __name__=="__main__":

	win = sg.Window('UAS-DTU Swarm Planner', home_layout, auto_size_text=True, default_element_size=(40, 1))

	while True:
		try:
			event, values = win.Read()

			if values!=None:
				print(values)
				params = list(values.values())
				dump_params_file = open("params","wb")
				pickle.dump(params,dump_params_file)
				dump_params_file.close()

			if event==None:
				continue

			if event=="Enable Ad-hoc Mode":
				Ad_hoc_thread = threading.Thread(target = Set_Ad_hoc_func)
				Ad_hoc_thread.start()

			elif event=="Disable Ad-hoc Mode":
				Disable_ad_hoc_thread = threading.Thread(target = Disable_Ad_hoc_func)
				Disable_ad_hoc_thread.start()

			elif event=="Test connections":
				Test_connections_thread = threading.Thread(target = Test_connections_func)
				Test_connections_thread.start()

			elif event=="Land All UAVs":
				Land_thread = threading.Thread(target = Land_func)
				Land_thread.start()

			elif event=="Plan Mission":
				Plan_mission_thread = threading.Thread(target = Plan_mission_func)
				Plan_mission_thread.start()
							
			elif event=="Save Waypoints":
				Save_wp_thread = threading.Thread(target = Save_wp_func)
				Save_wp_thread.start()

			elif event=="Kill Map":
				signal.SIGINT
				#signal.pthread_kill(ID, 9)
				#Kill_Map_thread = threading.Thread(target = Kill_map_func)	#Probably wont require any threading to do it.
				#Kill_Map_thread.start()

			elif event=="Plan Formation":
				plan_formation_thread = threading.Thread(target = Plan_formation_func)
				plan_formation_thread.start()
				print("it worked")
				#plan_formation_thread.join()
				
			elif event=="Upload Mission":
				upload_mission_thread = threading.Thread(target = Upload_mission_func)
				upload_mission_thread.start()
				
			elif event=="Start Mission":
				start_mission_thread = threading.Thread(target = Start_mission_func)
				start_mission_thread.start()
				
		except Exception as err:
			print("fuck it crashed"+ str(err))
			event, values  = win.Read()