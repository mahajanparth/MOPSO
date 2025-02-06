import socket
import multiprocessing
import dronekit
from scipy.spatial import distance
import subprocess
import os
import sys
import time
import json
import pickle
import datetime

try:
    path=sys.argv[1]
    sysid=sys.argv[2]
    os.chdir(path)
except:
    sysid=0
    #os.chdir("/home/uas-dtu/Desktop/new_on_uav")


engine_servo = "8"
pwm_value=0
def return_engine_servo_pwm(self, name, msg):
    global pwm_value
    global engine_servo
    msg_dict = msg.to_dict()
    #print (msg_dict)
    dict_key = "servo%s_raw" % (str(engine_servo))
    servo_pwm = msg_dict[dict_key]
    pwm_value=servo_pwm


class uav_server():
    def __init__(self,sys_id=0, connection_string="127.0.0.1:14554"):
        self.send_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        try:

            print("BEFORE VEHICLE")
            self.vehicle = dronekit.connect(connection_string)
            print("VEHICLE_CONNECTED")
            if sys_id != 0:

                self.sys_id=int(sys_id)
            else:

                self.sys_id = int(self.vehicle.parameters['SYSID_THISMAV'])
            print("SYSID",self.sys_id)

        except Exception as err :
            print("TRYING AGAIN",err)
            while True:
                try:
                    print("GETTING_SYSID")
                    self.sys_id = int(self.vehicle.parameters['SYSID_THISMAV'])
                    print("SYSID",self.sys_id)
                    break
                except Exception as err :
                    print("TRYING AGAIN",err)
                
        
        self.takeoff = False
        self.payload = False
        self.feed=False
        self.dtc=True
        self.uav_dict={"INTEL":{},"DTC":{}}
        self.last_timestamp=0

        self.gcsaddress_list = []
        self.engine_state = "LOW"
        #my_ip = ("192.168.4." + str(100 + self.sys_id), 20000)
        my_ip=("0.0.0.0",20000)
        
        print("my_ip", my_ip)
        self.refresh_file()
        print(self.uav_dict,self.gcsaddress_list)

        #self.gcs_address = (self.gcs_ip, 20010)
        self.recv_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_soc.bind(my_ip)

        self.send_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.send.soc.bind(my_ip)
        self.engine_servo = "8"
        self.pwm_value = 0



        self.vehicle.add_message_listener("SERVO_OUTPUT_RAW", return_engine_servo_pwm)

        self.start_server()

    def return_engine_servo_pwm(self, name, msg):

        msg_dict = msg.to_dict()
        print(msg_dict)
        dict_key = "servo%s_raw" % (self.engine_servo)
        servo8_pwm = msg_dict[dict_key]
        print("HELLO", servo8_pwm)
        self.pwm_value = servo8_pwm

    def refresh_file(self):
        with open("./uav_list.txt", "r+") as file_hd:
            lines = file_hd.readlines()

        for line in lines:
            data=line.strip().split()
            try:

                gcs_or_uav=data[0]
                ip=data[1]
                host_name=data[2]
                password=data[3]
                baud=data[4]
                interface=data[5]
                wifi_group = data[6]
                s_id=data[7]
            except:
                gcs_or_uav = "UAV"
                ip = "192.168.4.69"
                host_name = "uas-dtu"
                password = "Aether"
                baud = 57600
                interface = "INTEL"
            uav_id = int(ip.split(".")[3]) % 100  # self note : weak logic think something else

            if gcs_or_uav.upper() == "GCS":
                self.gcsaddress_list.append((ip,20010))
                #self.gcs_ip = ip
            else:

                if int(uav_id) ==int(self.sys_id):  # exclude it's own ip from uav list
                    if interface.upper()=="DTC":
                        self.dtc=True
                    else:
                        self.dtc=False
                    continue
                else:
                    if interface.upper() == "DTC":
                        self.uav_dict["DTC"][uav_id] = (ip,20000)
                    elif interface.upper() == "INTEL" :
                        self.uav_dict["INTEL"][uav_id] = (ip,20000)


    def set_servo(self, vehicle, servo_number, pwm_value):
        pwm_value_int = int(pwm_value)
        msg = vehicle.message_factory.command_long_encode(
            0, 0,
            dronekit.mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            servo_number,
            pwm_value_int,
            0, 0, 0, 0, 0
        )
        for i in range(3):
            vehicle.send_mavlink(msg)

    def send_data_to_other_uavs(self,dt,addr):
        app_json = json.dumps(dt).encode("UTF-8")
        self.send_soc.sendto(app_json, addr)


    def process_data(self, dt):
        global pwm_value
        global engine_servo
        li = ["STATE", "LAND", "RTL","STABILIZE", "TAKEOFF", "FEED", "ARM", "DISARM", "PAYLOAD","STABILIZED.ARM","ENGINE.HIGH","ENGINE.MID","ENGINE.LOW","PING","REBOOTPIX","UPDATE","TIME","MODE","SETSERVO","READSERVO"]
        print(dt)
        print("1700")


        data=dt["MESSAGE"]
        UAV_ID=int(dt["SYS_ID"])
        payload=dt["PAYLOAD"]
        packet_num=dt["PACKET_NO"]
        time_stamp=dt["TIMESTAMP"]

        if data.upper()=="DROP":
            self.payload = True
            dt["SYS_ID"] = self.sys_id
            dt["MESSAGE"] = "PAYLOAD"
            if self.payload == False:
                return " NOT DROPPED"
            else:

                print("1700")
                self.set_servo(self.vehicle, 7, 1700)
                #print("1100")
                #self.set_servo(self.vehicle, 7, 1100)
                #print("1900")
                #self.set_servo(self.vehicle, 7, 1900)
                #print("1100")
                #self.set_servo(self.vehicle, 7, 1100)
                return "DROPPED"

        if data.upper() == "REQUEST_TIME":
            dt["SYS_ID"] = self.sys_id
            dt["MESSAGE"] = "REQUEST_TIME"
            return "REQUEST_TIME"

        elif data.upper()=="CAMERA_DISCONNECTED":
            dt["SYS_ID"] = self.sys_id
            dt["MESSAGE"] = "CAMERA_DISCONNECTED"
            return "CAMERA_DISCONNECTED"

        elif data.upper()=="CAMERA_CONNECTED":
            dt["SYS_ID"] = self.sys_id
            dt["MESSAGE"] = "CAMERA_CONNECTED"
            return "CAMERA_CONNECTED"

        elif data.upper() == "ADHOC":
            dt["SYS_ID"] = self.sys_id
            dt["MESSAGE"] = "ADHOC"
            return dt["PAYLOAD"]

        if UAV_ID != self.sys_id:
            if "BROADCAST" in data.upper():
                if time_stamp < self.last_timestamp:
                    print("REJECTED")
                    return None
                else:
                    self.last_timestamp = time_stamp

                    if self.dtc:
                        for key in self.uav_dict["INTEL"].keys():
                            self.send_data_to_other_uavs(dt,self.uav_dict["INTEL"][key])
                        return None

                    else:
                        if UAV_ID in self.uav_dict["INTEL"].keys():
                            self.send_data_to_other_uavs(dt, self.uav_dict["INTEL"][UAV_ID])
                        return None
            elif "ROUTING" in data.upper():
                if time_stamp < self.last_timestamp:
                    print("REJECTED")
                    return None
                else:
                    self.last_timestamp = time_stamp

                    if self.dtc:
                        if UAV_ID in self.uav_dict["INTEL"].keys():
                            self.send_data_to_other_uavs(dt, self.uav_dict["INTEL"][UAV_ID])
                        return None

            elif "RETURN" in data.upper():
                if self.dtc:
                    for gcs_address in self.gcsaddress_list:
                        try:

                            app_json = json.dumps(dt).encode("UTF-8")
                            self.send_soc.sendto(app_json,gcs_address)
                            #print("sending message",gcs_address,message)
                        except Exception as err:
                            print("Error",err,gcs_address)
                    return None
                else:
                    # for now this is not executing //verify this
                    for key in self.uav_dict["DTC"].keys():
                        self.send_data_to_other_uavs(dt,self.uav_dict["DTC"][key])
                    return None
            elif "P2P" in data.upper():
                #do nothing here
                return None
        else:

            data = dt["MESSAGE"].split("_")[1]  # this is here to remove p2p ,broadcast or route from message to extract original message
            payload = dt["PAYLOAD"]
            packet_num = dt["PACKET_NO"]
            time_stamp = dt["TIMESTAMP"]

            if time_stamp < self.last_timestamp:
                print("REJECTED")
                return None
            else:
                self.last_timestamp = time_stamp

            if data.upper() in li:
                # used for updating mid flight
                if data.upper()=="TIME":

                    date_time = payload
                    os.system("echo Aether | sudo -S  date " + date_time)
                    return str(datetime.datetime.now())

                if data.upper()=="UPDATE":
                    #{"SWARM_PARAMETERS":{},"WAYPOINTS":[],"SWARM_TUNING_PARAMETERS":{},"TUNING_PARAMETERS":{},"COORDINATES":[],"GEOFENCE":[]}

                    coor_matrix=payload["COORDINATES"]
                    dump_coor_matrix_file = open("coor_matrix", "wb")
                    pickle.dump(coor_matrix, dump_coor_matrix_file)
                    dump_coor_matrix_file.close()

                    wp_list = payload["WAYPOINTS"]
                    dump_wp_file = open("wp_list", "wb")
                    pickle.dump(wp_list, dump_wp_file)
                    dump_wp_file.close()

                    send_list=payload["SWARM_PARAMETERS"]
                    dump_params_file = open("number_of_UAVs", "wb")
                    pickle.dump(send_list, dump_params_file)
                    dump_params_file.close()

                    weight_matrix = distance.cdist(coor_matrix,coor_matrix, 'euclidean')
                    dump_weight_matrix_file = open("weight_matrix", "wb")
                    pickle.dump(weight_matrix, dump_weight_matrix_file)
                    dump_weight_matrix_file.close()

                    return "UPDATED PARAMS"

                if data.upper()=="PING":
                    return "PINGING BACK"

                if data.upper() == "STATE":
                    uav_state = [self.sys_id,self.vehicle.mode.name,time.time(),time.time(),self.vehicle.location.global_frame.lat,self.vehicle.location.global_frame.lon,self.vehicle.location.global_relative_frame.alt,str(datetime.datetime.now())]

                    if self.vehicle.armed == False:
                        uav_state.append("DISARMED")
                    else:
                        uav_state.append("ARMED")

                    if self.takeoff == False:
                        uav_state.append("TAKEOFF READY")
                    else:
                        uav_state.append("SWARM CODE RUNNNING")

                    if self.feed == False:
                        uav_state.append("FEED INACTIVE")
                    else:
                        uav_state.append("FEED ACTIVE")

                    if self.payload == False:
                        uav_state.append("DROP_READY")
                    else:
                        uav_state.append("DROPPED")

                    uav_state.append(self.engine_state)
                    return str(uav_state)


                elif data.upper() == "LAND":
                    self.vehicle.mode = dronekit.VehicleMode("LAND")
                    self.vehicle.flush()


                    if self.vehicle.mode == dronekit.VehicleMode("LAND"):
                        self.takeoff=False
                        return "LAND SUCCESSFUL"
                    else:
                        return "LAND UNSUCESSFUL"

                elif data.upper() == "REBOOTPIX":
                    self.vehicle.reboot()
                    return "REBOOT COMMAND SEND TO PIXHAWK"

                elif data.upper() == "STABILIZE":
                    self.vehicle.mode = dronekit.VehicleMode("STABILIZE")
                    self.vehicle.flush()

                    if self.vehicle.mode == dronekit.VehicleMode("STABILIZE"):
                        return "STABILIZE SUCCESSFULLY "
                    else:

                        return "STABILIZE FAILED"

                elif data.upper() == "STABILIZED.ARM":
                    self.vehicle.mode = dronekit.VehicleMode("STABILIZE")
                    self.vehicle.armed=True
                    self.vehicle.flush()

                    if self.vehicle.mode == dronekit.VehicleMode("STABILIZE"):
                        return "STABILIZE SUCCESSFULLY ARMED"
                    else:

                        return "STABILIZE AND UNARMED"


                elif data.upper() == "RTL":
                    self.vehicle.mode = dronekit.VehicleMode("RTL")
                    self.vehicle.flush()
                    if self.vehicle.mode == dronekit.VehicleMode("RTL"):
                        self.takeoff=False
                        return "RTL SUCCESSFUL"
                    else:
                        return "RTL NOT SUCESSFUL"

                elif data.upper() == "TAKEOFF":
                    if self.takeoff == False:
                        try:
                            if payload:
                                var=str(payload)
                            else:
                                var="1"
                            command1 = "gnome-terminal -- python3 -u Swarm2.py "+str(self.sys_id) +" "+str(var)
                            Process = subprocess.check_call(command1 + " &", shell=True)
                            self.takeoff = True
                            return "STARTED_SWARMING "+var
                        except:
                            self.takeoff = False
                            return "FAILED_TAKEOFF "+var
                    else:
                        return "TAKEOFF CAN'T BE INITIATED AGAIN"


                elif data.upper() == "FEED":
                    print("STARTING FEED")
                    if self.feed==False:

                        try:

                            command2 = "gnome-terminal -- python3 ./VIDEO_STREAMER/Server.py "
                            Process2 = subprocess.check_call(command2 + " &", shell=True)
                            self.feed = True

                        except:
                            self.feed = False
                            return "FEED_STARTED"

                    else:
                        return "FEED CAN'T BE INITIATED AGAIN"

                elif data.upper() == "ARM":

                    self.vehicle.mode = dronekit.VehicleMode("GUIDED")
                    # print("GUIDED SUCCESSFUL")
                    self.vehicle.armed = True
                    self.vehicle.flush()
                    if self.vehicle.armed==True:
                        return "GUIDED AND ARMED"
                    else:
                        return "ARMING FAILED"

                elif data.upper() == "DISARM":
                    self.vehicle.armed = False
                    self.vehicle.flush()
                    return "DISARMED"

                elif data.upper() == "PAYLOAD":
                    self.payload=True
                    if self.payload == False:
                        return "DROP_READY"
                    else:
                        print("1700")
                        self.set_servo(self.vehicle, 7, 1700)
                        #print("1100")
                        #self.set_servo(self.vehicle, 7, 1100)
                        #print("1900")
                        #self.set_servo(self.vehicle, 7, 1900)
                        #print("1100")
                        #self.set_servo(self.vehicle, 7, 1100)
                        return "DROPPED"

                elif "ENGINE" in data.upper():
                    str1=data.upper()
                    _,state=str1.strip().split(".")

                    if state=="HIGH" :
                        self.engine_state="HIGH"
                        self.set_servo(self.vehicle, 8, 2000)
                        return "ENGINE SET TO HIGH"
                    elif state=="MID" :
                        self.engine_state = "MID"
                        self.set_servo(self.vehicle, 8, 1500)
                        return "ENGINE SET TO MID"
                    elif state=="LOW" :
                        self.engine_state = "LOW"
                        self.set_servo(self.vehicle, 8, 1100)
                        return "ENGINE SET TO LOW"

                elif "MODE" in data.upper():
                    mode=payload
                    self.vehicle.mode=dronekit.VehicleMode(mode)
                    self.vehicle.flush()
                    if self.vehicle.mode.name!=dronekit.VehicleMode(mode):
                        return "changing to mode "+str(mode)+" Failed"
                    else:
                        return "changing to mode " + str(mode) +" Sucesseded"
                elif "SETSERVO" in data.upper():
                    var=payload
                    engine_servo =str(var[0])
                    self.set_servo(self.vehicle, int(var[0]), int(var[1]))
                    return "Servo " +engine_servo+"set to "+str(pwm_value)
                elif "READSERVO" in data.upper():
                    var=payload
                    print(var)
                    engine_servo=str(var)
                    return "SERVO "+str(engine_servo) +"VALUE IS "+ str(pwm_value)


    def start_server(self):
        data={}
        data["MESSAGE"] = "RETURN"
        data["PAYLOAD"] = "REQUEST_TIME"
        data["SYS_ID"] = self.sys_id
        data["PACKET_NO"] = 0
        data["TIMESTAMP"] = 0
        self.set_servo(self.vehicle,7, 1100)
        
        for gcs_address in self.gcsaddress_list:
            # if address[0]== gcs_address[0] or self.dtc:
            try:
                app_json = json.dumps(data).encode("UTF-8")
                self.send_soc.sendto(app_json, gcs_address)
                print("sending message", gcs_address, data)
            except Exception as err:
                print("Error", err, gcs_address)

        
        while True:
            try:

                data, address = self.recv_soc.recvfrom(2048)
                data=json.loads(data) # data is a dictionary with MESSAGE, SYS_ID , PAYLOAD AS KEYS
                print("Data Received From",address)

                if data:

                    message = self.process_data(data)
                    print("MESSAGE ",message)
                    if message:
                        data["MESSAGE"] ="RETURN"
                        data["PAYLOAD"]=message

                        for gcs_address in self.gcsaddress_list:
                        #if address[0]== gcs_address[0] or self.dtc:
                            try:
                                app_json = json.dumps(data).encode("UTF-8")
                                self.send_soc.sendto(app_json, gcs_address)
                                print("sending message",gcs_address,message)
                            except Exception as err:
                                print("Error",err,gcs_address)


                    else:
                        continue


            except Exception as err:
                print(err)


if __name__ == "__main__":
    print("starting uav server")
    uav_server(sysid)
