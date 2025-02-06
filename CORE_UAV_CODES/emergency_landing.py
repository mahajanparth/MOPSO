import time
from dronekit import connect, VehicleMode
import subprocess
import sys

baudrate=int(sys.argv[1])
sysid=int(sys.argv[2])

print(baudrate)

try:
	subprocess.check_call("gnome-terminal -- mavproxy.py --master=/dev/ttyTHS1 --out=127.0.0.1:14552 ",shell=True)
except Exception as err:
	print(err)

time.sleep(5)
vehicle = connect("127.0.0.1:14552")
sys_id = sysid
while vehicle.mode.name !="LAND":
	vehicle.mode=VehicleMode("LAND")
	msg = "Vehicle " + str(sys_id) + " Returned"
	print(msg)
ip = 100 + sys_id
print("ip",ip)
