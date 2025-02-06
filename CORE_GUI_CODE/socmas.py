import socket
from scp import SCPClient
import paramiko
import time
import os


s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s[i].settimeout(2)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
address = ('127.0.0.1', 40000)
s.bind(address)
s.listen(1)
c, a = s.accept()
print (a)
time.sleep(5)
s.shutdown(1)
s.close()
