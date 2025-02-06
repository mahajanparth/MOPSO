import numpy as np
import time
import dronekit
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil

vehicle = list()
N = 5

for i in range(N):
    vehicle[i] = connect('/dev/ttyUSB'+str(i))

for i in range(N):
    vehicle[i].mode = VehicleMode("LAND")