import socket 
import os
import time
import netifaces as ni

no_of_uav=2
uavlist=list(range(211,211+no_of_uav))
connectionlist=list()

while (len(uavlist)!=0):

	for i in uavlist:
		server_ip="192.168.4.{0}".format(i)
		result=os.system('ping -c 1 ' + server_ip)

		if result==0:
			print ("connected to UAV ",(i%10) )
			uavlist.remove(i)
			connectionlist.append(i)
	print (connectionlist)
