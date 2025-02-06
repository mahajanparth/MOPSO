import dronekit

vehicle=dronekit.connect("127.0.0.1:14552")

while vehicle.mode.name!="LAND":
    vehicle.mode=dronekit.VehicleMode("LAND")

while True:
    mode=input("ENTER THE MODE YOU WANT TO FLICK")
    try:
        print(vehicle.mode.name)
        vehicle.mode=dronekit.VehicleMode(mode.upper())

    except Exception as err:
        print("ERROR",err)