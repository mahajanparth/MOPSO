import socket 
import os
import time
import netifaces as ni

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
#s.settimeout(0.5)
bound=0
while True:
	try: 
		s.connect(('127.0.0.1',40000))
		print ("connected")
		"""
		if result==0 and bound==0:
			print ("pinged")
			print ("not bound")
			#print ("connecting to ",(ground_host,ground_port))	
			s.connect(('127.0.0.1',40000))
			time.sleep(1)
			bound=1

		elif result != 0 and bound==1:
			print ("lossssssssssssssssssssssssssssssssssssssssssst")
			bound=0
			s.shutdown(1)	
			time.sleep(1)	

		elif result==0 and bound==1:
			print ("trying to recove##########################################################################")
			time.sleep(1)			
			if (s.recv(1024)=="c"):
				break
		else:
			time.sleep(1)
			print ("0000000000000000")
			continue		
		"""	
	except Exception as e:
		time.sleep(1)
		print e
		continue	
