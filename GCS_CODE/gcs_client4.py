import PySimpleGUI as sg
import paramiko
import time
import socket
import struct
from dronekit import connect, VehicleMode
import time
import multiprocessing
import json
import operator
import threading
import logging
import datetime

class multicast(object):
	def __init__(self):
		self.public_dict = {}
		# make these variables private

		# WiFi Adhoc Multicast Address
		self.multicast_addr = "239.0.0.0"
		self.bind_addr = "0.0.0.0"
		self.port = 6001

		# DTC Multicast Address
		self.dtc = True
		self.multicast_addr_dtc = "239.0.0.0"
		self.port_dtc = 6001

		# Data Packet Variables
		self.vehicle = None
		self.sleep_time = .05
		self.refresh_rate = 5
		self.packet_counter = 0
		self.vehicle_connection_string = "127.0.0.1:14550"
		self.local_bind_ip = "127.0.0.1"
		self.swarmrecv_port = 10000
		self.humanrecv_port = 10002

		self.swarm_send_ip = "127.0.0.1"
		self.swarm_send_port = 10001
		self.max_human_limit = 2
		self.was_filled = False
		self.gcs_addr = ("192.168.0.59", 11111)
		logging.basicConfig(filename="GCS_client3" + str(datetime.datetime.now()) + ".log",format=' %(module)s %(lineno)d %(message)s', filemode='w')

		self.logger = logging.getLogger()
		self.logger.setLevel(logging.INFO)

		try:
			# self.vehicle=connect(self.vehicle_connection_string)
			pass

		except Exception as err:
			self.vehicle = None
			print("EXCEPTION IN CONNECTING TO UAV " + str(err))

		self.main_thread()

	def create_sender_socket(self):
		print("creating sender socket")
		try:
			send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			# sock.settimeout(.2)

			ttl = struct.pack('b', 1)
			# configuring socket in os in multicast mode
			send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
			return send_sock
		except Exception as err:
			print("create_sender_socket" + str(err))
			return None

	def create_and_bind_receiver_socket(self, MulticastAddress, Port):
		try:

			recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			# membership = socket.inet_aton(self.multicast_addr) + socket.inet_aton(self.bind_addr)

			recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			membership = socket.inet_aton(MulticastAddress) + socket.inet_aton(self.bind_addr)

			# group = socket.inet_aton(self.multicast_addr)
			# mreq = struct.pack("4sl", group, socket.INADDR_ANY)
			recv_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.bind_addr))

			recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
			# self.recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

			recv_sock.bind((self.bind_addr, Port))
			return recv_sock
		except Exception as err:
			print("create_receiver_socket" + str(err))
			print(err)
			return None

	def recv_dtc(self, dt):
		static_dict = {}
		modes = ["RTL", "LAND"]
		start_time=time.time()
		while True:

			shared_dt = dt["DICT"]
			arr = set(dt["NEW_UAV"])
			packet_counter=dt["PACKET_COUNTER"]

			try:

				message, address = self.recv_sock.recvfrom(1024)

				data = json.loads(message.decode('utf-8'))
				uav_id = int(data["SYSID"])
				data["RECVTIME"] = time.time()
				key = uav_id

				if int(key) not in static_dict.keys():
					static_dict[int(key)] = data
					static_dict[int(key)]["RECVTIME"] = time.time()
					packet_counter[int(key)]=0
					if data["MODE"] not in modes:

						if int(key) not in shared_dt.keys():
							shared_dt[int(key)] = data
							shared_dt[int(key)]["RECVTIME"] = time.time()
							static_dict[int(key)] = data
							static_dict[int(key)]["RECVTIME"] = shared_dt[int(key)]["RECVTIME"]
							arr.add(int(key))

						elif data["SENDTIME"] > shared_dt[int(key)]["SENDTIME"]:
							arr.add(int(key))
							shared_dt[int(key)] = data
							shared_dt[int(key)]["RECVTIME"] = time.time()
							static_dict[int(key)] = data
							static_dict[int(key)]["RECVTIME"] = shared_dt[int(key)]["RECVTIME"]
						# print("newpacket", key)
						else:
							# print("Neglecting Late packet")
							pass
				else:
					# print("PANO 1 : ", data[key]["SENDTIME"], " PANO 2: ", shared_dt[key]["SENDTIME"])

					if data["SENDTIME"] > static_dict[int(key)]["SENDTIME"]:
						static_dict[int(key)] = data
						static_dict[int(key)]["RECVTIME"] = time.time()
						packet_counter[int(key)] += 1
						if data["MODE"] not in modes:
							if int(key) not in shared_dt.keys():
								shared_dt[int(key)] = data
								shared_dt[int(key)]["RECVTIME"] = time.time()
								static_dict[int(key)] = data
								static_dict[int(key)]["RECVTIME"] = shared_dt[int(key)]["RECVTIME"]
								arr.add(int(key))

							elif data["SENDTIME"] > shared_dt[int(key)]["SENDTIME"]:
								arr.add(int(key))
								shared_dt[int(key)] = data
								shared_dt[int(key)]["RECVTIME"] = time.time()
								static_dict[int(key)] = data
								static_dict[int(key)]["RECVTIME"] = shared_dt[int(key)]["RECVTIME"]
							# print("newpacket", key)
							else:
								# print("Neglecting Late packet")
								pass

					# print("******* DATA RECEIVED INTEL ******",uav_id)
					else:
						# data not adding in shared list if mode land or RTL
						pass
			except Exception as err:
				print("recv_package " + str(err))

				self.recv_sock.close()
				self.recv_sock = self.create_and_bind_receiver_socket(self.multicast_addr, self.port)

			# check if a data is in the dictionary for more than refresh sec
			try:

				shared_dt = {key: data for (key, data) in shared_dt.items() if
							 time.time() - data["RECVTIME"] < self.refresh_rate}
			except Exception as err:
				# print("Error in recv pack",err)
				pass
			if time.time() -start_time >1:
				start_time=time.time()
				for key in packet_counter.keys():
					packet_counter[key]=0


			dt["DICT"] = shared_dt
			dt["STATIC_DICT"] = static_dict
			dt["PACKET_COUNTER"]=packet_counter
	def send_to_swarmcontroller(self, sock, dict):

		try:

			app_json = json.dumps(dict, sort_keys=True).encode("UTF-8")
			sock.sendto(app_json, (self.swarm_send_ip, self.swarm_send_port))
			#print("Data sent to swarm_code")


		except Exception as err:
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			print("Error in send to swarmcontroller", err)

	def recv_from_swarmcontroller(self, sock):
		sock.settimeout(1)
		while True:

			try:

				bin_str = sock.recv(2048)
				dt = json.loads(bin_str.decode('utf-8'))
				print(".....DATA_RECEIVED FROM SWARM..........")
				self.recv_dt = dt

			except Exception as err:
				print("No Data Received from swarm_code " + str(err))

	def clear_shared_list(self, dt, threshlod_time, was_filled):
		while True:
			shared_dt = dt["DICT"]
			arr=set(dt["NEW_UAV"])
			if shared_dt == None or shared_dt == {}:
				time.sleep(1)
				continue
			try:
				was_filled.value = 1
				for key,data in shared_dt.items():
					if time.time() - data["TIMESTAMP"] < threshlod_time:
						shared_dt[key]=data
					else:
						if int(key) in arr:
							arr.remove(int(key))
				#print("Clearing DICT",arr)
			except Exception as err:
				print("Error in clearing list ", err)
			dt["DICT"] = shared_dt
			dt["NEW_UAV"]=arr
			time.sleep(self.sleep_time)

	def main_thread(self):

		# Create WiFi Adhoc Multicast
		self.send_sock = self.create_sender_socket()
		if self.send_sock is None:
			self.send_sock = self.create_sender_socket()

		self.recv_sock = self.create_and_bind_receiver_socket(self.multicast_addr, self.port)
		self.recv_sock.settimeout(0.1)

		if self.recv_sock is None:
			self.recv_sock = self.create_and_bind_receiver_socket(self.multicast_addr, self.port)
			self.recv_sock.settimeout(0.1)

		with multiprocessing.Manager() as manager:

			shared_dict = manager.dict({"DICT": {},"STATIC_DICT":{}, "NEW_UAV":[],"PACKET_COUNTER":{}})
			self.was_filled = multiprocessing.Value("i", 0)
			self.SYS_ID=multiprocessing.Value("i", 0)

			if self.dtc:
				recv_dtc_process = multiprocessing.Process(target=self.recv_dtc, args=[shared_dict])

			if self.dtc:
				recv_dtc_process.start()
				print("WORING_DTC")
			swarm_send_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			# swarm_send_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			"""
			swarm_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			swarm_recv_sock.bind((self.local_bind_ip, self.swarmrecv_port))
			swarm_recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			"""
			num_of_uav=26
			home_layout =[
					[sg.Text('INDICATOR', size=(22, 1), font=("Helvetica", 25), text_color='#033F63', justification='left')],
					[sg.Text('_' * 30, size=(40, 1), justification='center')]
					]
			packet_counter=shared_dict["PACKET_COUNTER"]
			uav_data_layout=[[sg.Column([[sg.Text('UAV '+ str(i), size=(15,1), font=("Helvetica",8), text_color='#033F63', justification='left', key='text'+ str(i)), 
			sg.Button('land', button_color=('red', '#EE6C4D'), key='button' + str(i)),
			sg.Button('NOT UPDATING', button_color=('red', '#EE6C4D'), key='packet' + str(i)),
			sg.Button('frequency', button_color=('red', '#EE6C4D'), key='FREQUENCY' + str(i)),
			sg.Button('DELAY', button_color=('red', '#EE6C4D'), key='DELAY' + str(i))]], key="col" + str(i)) ]for i in range(1,num_of_uav)]

			home_layout+=uav_data_layout

			win = sg.Window('gcs_client2', home_layout, auto_size_text=True, default_element_size=(30, 1)).Finalize()
			for i in range(1,num_of_uav):
				win.Element("col"+str(i)).Update(visible=False)

			start_time=time.time()
			while True:
				temp = shared_dict["STATIC_DICT"].copy()
				packet_counter = shared_dict["PACKET_COUNTER"]
				# print("........SHARED..........", shared_dict)
				print("######...MAIN...#####", [key for key in sorted(temp.keys())])
				[print(key, " :: ", temp[key]) for key in sorted(temp.keys())]
				self.logger.info(str(temp))
				self.send_to_swarmcontroller(swarm_send_sock, temp)
				# temp=self.recv_from_swarmcontroller(swarm_recv_sock,temp)
				#shared_dict["DICT"] = temp

				for key in packet_counter.keys():
					win.Element("FREQUENCY" + str(key)).update(str(shared_dict["PACKET_COUNTER"][key]),
															   button_color=('white', 'green'))

					win.refresh()

				try:
					for key in sorted(temp.keys()):
						#win.Element("FREQUENCY"+str(key)).update(str(shared_dict["PACKET_COUNTER"][key][0]/(time.time()-start_time)),button_color=('white', 'green'))
						win.Element("DELAY" + str(key)).update(str(shared_dict["STATIC_DICT"][key]["RECVTIME"]- shared_dict["STATIC_DICT"][key]["SENDTIME"] ), button_color=('white', 'green'))



						if temp[key]["MODE"] not in ['RTL','LAND']:
							win.Element('button'+str(key)).update(temp[key]["MODE"],button_color=('white', 'green'))
						else:
							win.Element('button'+str(key)).update(temp[key]["MODE"],button_color=('white', 'red'))

						if time.time()-temp[key]["RECVTIME"] < self.refresh_rate:
							win.Element('packet'+str(key)).update(temp[key]["PACKETNO"],button_color=('white', 'green'))
						else:
							win.find_element('packet'+str(key)).update(temp[key]["PACKETNO"],button_color=('white', 'red'))

						win.Element("col"+str(key)).Update(visible=True)
						win.Refresh()

				except Exception as err:
					print("Error",err)



			


if __name__ == "__main__":

	multicast()