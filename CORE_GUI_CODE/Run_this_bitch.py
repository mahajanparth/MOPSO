import PySimpleGUI as sg
import os
from GUI import graphic
from multiprocessing import Process
from scipy.spatial import distance
import matplotlib.pyplot as plt
import matplotlib
import tkinter as Tk
import numpy as np
import threading
import dronekit
from dronekit import connect
import socket
from time import sleep
import netifaces as ni
from scp import SCPClient
import paramiko

global graphic_object
graphic_object = graphic()

def plan_formation_func():
	d = graphic_object.display()
	print(d)

def plan_mission_func():
	os.chdir("/home/aniket/ardupilot/ArduCopter")
	os.system("sim_vehicle.py -L L1 --map -w")

def Test_connections_func():
	os.chdir("/home/aniket/IAF/GUI")
	os.system("python test_connections.py")

def upload_mission_func():
	os.chdir("/home/aniket/IAF/GUI")
	os.system("python upload_mission.py")

def start_mission_func():
	os.chdir("/home/aniket/IAF/GUI")
	os.system("python start_mission.py")

def Set_Ad_hoc_func():
	os.chdir("/home/aniket/IAF/GUI")
	os.system("gnome-terminal -e bash set_adhoc_gcs.sh")

def Disable_Ad_hoc_func():
	os.chdir("/home/aniket/IAF/GUI")
	os.system("gnome-terminal -e bash revert_adhoc_gcs.sh")

def Land_func():
	os.chdir("/home/aniket/IAF/GUI")
	os.system("python LAND_ALL_UAVS.py")

home_layout = [[sg.Text('Swarm Planner', size=(22, 1), font=("Helvetica", 25), text_color='#033F63',justification='left'), sg.Image("logo_50.png")],
	[sg.Text('='  * 100, size=(80, 1), justification='center')],
	[sg.Text('Enter the Number of UAVs',size=(36,1),justification='right'), sg.InputText()],
	[sg.Text('Enter the UAV_ID that will remain in front',size=(36,1),justification='right'), sg.InputText()],
	[sg.Text('Enter the minimum distance between UAVs',size=(36,1),justification='right'), sg.InputText()],
	[sg.Text('_'  * 100, size=(80, 1), justification='center')],
	[sg.Button('Enable Ad-hoc Mode', button_color=('white', '#033F63')), sg.Button('Disable Ad-hoc Mode', button_color=('white', '#033F63')), sg.Button('Land All UAVs', button_color=('white', '#EE6C4D'))],
	[sg.Button('Plan Mission', button_color=('white', '#033F63')), sg.Button('Plan Formation', button_color=('white', '#033F63')), sg.Button('Test connections', button_color=('white', '#033F63')), sg.Button('Upload Mission', button_color=('white', '#033F63'))],
	[sg.Text('_'  * 100, size=(80, 1), justification='center')],
	[sg.Button('Start Mission', button_color=('white', 'green'))]]


if __name__=="__main__":

	win = sg.Window('UAS-DTU Swarm Planner', home_layout, auto_size_text=True, default_element_size=(40, 1))

	while True:
		try:
			event, values = win.Read()

			if values!=None:
				print(values)

			if event==None:
				continue

			if event=="Plan Mission":
				plan_mission_thread = threading.Thread(target = plan_mission_func)
				plan_mission_thread.start()
			
			elif event=="Plan Formation":
				plan_formation_thread = threading.Thread(target = plan_formation_func)
				plan_formation_thread.start()
				print("it worked")
				#plan_formation_thread.join()

			elif event=="Enable Ad-hoc Mode":
				Ad_hoc_thread = threading.Thread(target = Set_Ad_hoc_func)
				Ad_hoc_thread.start()
			
			elif event=="Disable Ad-hoc Mode":
				Anti_ad_hoc_thread = threading.Thread(target = Disable_Ad_hoc_func)
				Anti_ad_hoc_thread.start()
			
			elif event=="Land All UAVs":
				Land_thread = threading.Thread(target = Land_func)
				Land_thread.start()

			elif event=="Test connections":
				Test_connections_thread = threading.Thread(target = Test_connections_func)
				Test_connections_thread.start()
				
			elif event=="Upload Mission":
				upload_mission_thread = threading.Thread(target = upload_mission_func)
				upload_mission_thread.start()
				
			elif event=="Start Mission":
				start_mission_thread = threading.Thread(target = start_mission_func)
				start_mission_thread.start()
				

		except Exception as err:
			print("fuck it crashed"+ str(err))
			event, values  = win.Read()