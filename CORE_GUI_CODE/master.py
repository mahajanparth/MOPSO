import socket
from scp import SCPClient
import paramiko
import time
file = open('no_of_uav_groundip.txt', 'r')
no_of_uav=int(file.readline().rstrip())
host=str(file.readline().rstrip())
port=int(file.readline())
uavlist=list(range(211,211+no_of_uav))
nextline=file.readline()


def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

if (nextline!=""):
	discardlist=(nextline.rstrip()).split(",")
	discardlist=map(int,discardlist)
	for i in (discardlist):
		if (i in uavlist):
			uavlist.remove(i)

no_of_uav=len(uavlist)
s=list()
conn=list()
addr=list()
for i in range(0,len(uavlist)):
    print ("Waitng for connection with UAV == ",(uavlist[i]%10))
    s.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    #s[i].settimeout(1)
    s[i].bind((host, port+i+1))
    s[i].listen(1)
    c, a = s[i].accept()
    conn.append(c)
    addr.append(a)
    print ("Connected To follower  == ", addr[i])

print ("connected to all")

readylist=list()
for i in range (no_of_uav):
	if (i not in readylist):
		try:
			data=conn[i].recv(1024)
			if (data=="ready"):
				uavlist[i]=0
				readylist.append(i)
				print ("Ready list =",readylist)
		except:
			continue
	if (len(readylist)==no_of_uav):
		break	

for i in range(len(uavlist)):
	conn[i].send("start")
print ("Started")	
file.close()



