
import socket 
import os
import time
import netifaces as ni

file = open('no_of_uav_groundip.txt', 'r')
no_of_uav = int(file.readline())
ground_host=file.readline().rstrip()
groundip=(ground_host.split("."))[-1]
ni.ifaddresses('wlan1')
myip = ni.ifaddresses('wlan1')[ni.AF_INET][0]['addr']
myself=int((myip.split("."))[-1])
ground_port=int(file.readline())+(myself%10)
uavlist=list(range(211,211+no_of_uav))
uavlist.remove(myself)
nextline=file.readline()
if (nextline!=""):
	discardlist=(nextline.rstrip()).split(",")
	discardlist=map(int,discardlist)
	for i in (discardlist):
		if (i in uavlist):
			uavlist.remove(i)
print (uavlist)
no_of_uav=len(uavlist)

os.system("lxterminal -e bash -c \"python send_data_udp_dronekit.py; exec bash\"&")
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.settimeout(0.5)
bound=0
count=0
while True:
	try: 
		server_ip="192.168.4.{0}".format(groundip)
		result=os.system('ping -c 1 ' + server_ip)
		print result

		if result==0 and bound==0:
			print ("pinged")
			print ("not bound")
			print ("connecting to ",(ground_host,ground_port))	
			s.connect((ground_host,ground_port))
			bound=1

		elif result != 0 and bound==1:
			print ("lossssssssssssssssssssssssssssssssssssssssssst")
			bound=0
			s.close()
			del s
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			s.settimeout(0.5)		

		elif result==0 and bound==1:
			time.sleep(1)
			count+=1
			print ("trying to recove##########################################################################")
			if (s.recv(1024)=="c"):
				break

		else:
			bound=0
			print ("0000000000000000")
			continue		
			
	except Exception as e:
		print ("ddddddddddddddddddddddddddddddddddddddddddd",count)
		if count == 5:
			count=0
			bound=0	
		s.close()
		del s
		s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		s.settimeout(0.5)
		time.sleep(1)
		print e
		continue	

while (len(uavlist)!=0):

	for i in uavlist:
		server_ip="192.168.4.{0}".format(i)
		result=os.system('ping -c 1 ' + server_ip)

		if result==0:
			uavlist.remove(i)
			print ("removed {0}".format(i))
			
print ("connected to all")			
s.send("ready")

data= s.recv(1024)

if data=="start":
	os.system("lxterminal -e bash -c \"python Flite_code.py; exec bash\"&")
file.close()
s.close()
