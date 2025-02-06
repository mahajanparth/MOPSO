from scp import SCPClient
import paramiko


file = open('no_of_uav_groundip.txt', 'r')
no_of_uav=int(file.readline().rstrip())
host=str(file.readline().rstrip())
port=int(file.readline())
uavlist=list(range(211,211+no_of_uav))
nextline=file.readline()
if (nextline!=""):
	discardlist=(nextline.rstrip()).split(",")
	discardlist=map(int,discardlist)
	for i in (discardlist):
		if (i in uavlist):
			uavlist.remove(i)
print uavlist
no_of_uav=len(uavlist)

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client



for i in uavlist:
	#print ("sending to UAV", (i%10))
	ssh = createSSHClient("192.168.4.{0}".format(i),22,"pi","raspberry")
	scp = SCPClient(ssh.get_transport())
	scp.put('connectiontest1.py','connectiontest1.py')
	scp.put('no_of_uav_groundip.txt','no_of_uav_groundip.txt')
	scp.put('start.py','start.py')
	print ("sent to UAV ",(i%10))

