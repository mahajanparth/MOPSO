import socket
import struct
from dronekit import connect, VehicleMode
import time
import multiprocessing
import json
import threading
import logging
import datetime
import os
import sys

class multicast(object):
    def __init__(self, sysid):
        self.sysid = sysid
        self.public_dict = {}
        # make these variables private

        # WiFi Adhoc Multicast Address
        self.multicast_addr = "239.0.0.0"
        self.bind_addr = "0.0.0.0"
        self.port = 6001

        # Data Packet Variables
        self.vehicle = None
        self.sleep_time = .05
        self.refresh_rate = 1
        self.packet_counter = 0
        self.vehicle_connection_string = "127.0.0.1:14550"
        self.local_bind_ip = "127.0.0.1"
        self.swarmrecv_port = 10000
        self.humanrecv_port = 10002
        self.swarm_send_ip = "127.0.0.1"
        self.swarm_send_port = 10001
        self.local_ip = "127.0.0.1"
        self.local_server_port = 20000
        self.max_human_limit = 2
        self.was_filled = False
        files = os.listdir("modifiedserverlogs")
        logging.basicConfig(filename="modifiedserverlogs/logs_modified_server8" + str(len(files)) + ".log",format=' %(module)s %(lineno)d %(asctime)s %(message)s', filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.main_thread()

    def create_sender_socket(self):
        print("creating sender socket")
        try:
            send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            # sock.settimeout(.2)

            ttl = struct.pack('b', 1)
            # configuring socket in os in multicast mode
            send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            return send_sock
        except Exception as err:
            print("create_sender_socket" + str(err))
            return None

    def create_and_bind_receiver_socket(self, multicastAddress, port):
        try:

            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            # membership = socket.inet_aton(self.multicast_addr) + socket.inet_aton(self.bind_addr)

            recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            membership = socket.inet_aton(multicastAddress) + socket.inet_aton(self.bind_addr)

            # group = socket.inet_aton(self.multicast_addr)
            # mreq = struct.pack("4sl", group, socket.INADDR_ANY)
            recv_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.bind_addr))

            recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
            # self.recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            recv_sock.bind((self.bind_addr, port))
            return recv_sock
        except Exception as err:
            print("create_receiver_socket" + str(err))
            print(err)
            return None

    def get_encoded_telemetry(self):

        if self.vehicle is not None:

            lat = self.vehicle.location.global_frame.lat
            lon = self.vehicle.location.global_frame.lon
            alti = self.vehicle.location.global_relative_frame.alt
            heading = self.vehicle.heading
            # uav_id = int(self.vehicle.parameters['SYSID_THISMAV'])
            uav_id = self.sysid
            mode = self.vehicle.mode.name
            self.packet_counter += 1
            # data = str(uav_id)+" "+str(lat) + " " + str(lon)+ " "+str(alti)+" "+str(self.packet_counter)
            # message = data.encode("utf-8")
            message = [uav_id, mode, lat, lon, heading, alti, self.packet_counter]

            return message
        else:

            try:
                # self.vehicle = connect(self.vehicle_connection_string)
                lat = self.vehicle.location.global_frame.lat
                lon = self.vehicle.location.global_frame.lon
                alti = self.vehicle.location.global_relative_frame.alt
                heading = self.vehicle.heading
                # uav_id = int(self.vehicle.parameters['SYSID_THISMAV'])
                uav_id = self.sysid
                mode = self.vehicle.mode.name
                self.packet_counter += 1
                # data = str(uav_id)+" "+str(lat) + " " + str(lon)+ " "+str(alti)+" "+str(self.packet_counter)
                # message = data.encode("utf-8")
                data = [uav_id, mode, lat, lon, heading, alti, self.packet_counter]

                # data = str(lat) + " " + str(lon)
                # message = data.encode("utf-8")

                return data
            except Exception as err:
                self.vehicle = None
                print("Exception encountered in get_encoded_telemetry", str(err))
                return None

    def recv_packets(self, dt):
        static_dict = {}
        modes = ["GUIDED"]
        while True:

            shared_dt = dt["DICT"]
            arr = set(dt["NEW_UAV"])

            try:

                message, address = self.recv_sock.recvfrom(1024)

                data = json.loads(message.decode('utf-8'))
                uav_id = int(data["SYSID"])
                data["RECVTIME"] = time.time()
                key = uav_id

                if int(key) not in static_dict.keys():
                    static_dict[int(key)] = data
                    static_dict[int(key)]["RECVTIME"] = time.time()
                    if data["MODE"] in modes:

                        if int(key) not in shared_dt.keys():
                            shared_dt[int(key)] = data
                            shared_dt[int(key)]["RECVTIME"] = time.time()
                            static_dict[int(key)] = data
                            static_dict[int(key)]["RECVTIME"] = shared_dt[int(key)]["RECVTIME"]
                            arr.add(int(key))

                        elif data["SENDTIME"] > shared_dt[int(key)]["SENDTIME"]:
                            arr.add(int(key))
                            shared_dt[int(key)] = data
                            shared_dt[int(key)]["RECVTIME"] = time.time()
                            static_dict[int(key)] = data
                            static_dict[int(key)]["RECVTIME"] = shared_dt[int(key)]["RECVTIME"]
                            # print("newpacket", key)
                        else:
                            # print("Neglecting Late packet")
                            pass
                else:
                    # print("PANO 1 : ", data[key]["SENDTIME"], " PANO 2: ", shared_dt[key]["SENDTIME"])

                    if data["SENDTIME"] > static_dict[int(key)]["SENDTIME"]:
                        static_dict[int(key)] = data
                        static_dict[int(key)]["RECVTIME"] = time.time()
                        if data["MODE"] in modes:
                            if int(key) not in shared_dt.keys():
                                shared_dt[int(key)] = data
                                shared_dt[int(key)]["RECVTIME"] = time.time()
                                static_dict[int(key)] = data
                                static_dict[int(key)]["RECVTIME"] = shared_dt[int(key)]["RECVTIME"]
                                arr.add(int(key))

                            elif data["SENDTIME"] > shared_dt[int(key)]["SENDTIME"]:
                                arr.add(int(key))
                                shared_dt[int(key)] = data
                                shared_dt[int(key)]["RECVTIME"] = time.time()
                                static_dict[int(key)] = data
                                static_dict[int(key)]["RECVTIME"] = shared_dt[int(key)]["RECVTIME"]
                                # print("newpacket", key)
                            else:
                                # print("Neglecting Late packet")
                                pass

                    # print("******* DATA RECEIVED INTEL ******",uav_id)
                    else:
                        # data not adding in shared list if mode land or RTL
                        pass
            except Exception as err:
                print("recv_package " + str(err))

                self.recv_sock.close()
                self.recv_sock = self.create_and_bind_receiver_socket(self.multicast_addr, self.port)

            # check if a data is in the dictionary for more than refresh sec
            try:

                shared_dt = {key: data for (key, data) in shared_dt.items() if time.time() - data["RECVTIME"] < self.refresh_rate}
            except Exception as err:
                # print("Error in recv pack",err)
                pass

            dt["DICT"] = shared_dt
            dt["STATIC_DICT"] = static_dict

    def send_packets(self, dt, was_filled):
        # Trying to connect to vehicle again
        try:

            self.vehicle = connect(self.vehicle_connection_string)
            uav_id, mode, lat, lon, heading, alti, packet_counter = self.get_encoded_telemetry()
        except Exception as err:
            print("Error", err)   # SYSID GIVING ERRORS
            while True:
                print("TRYING AGAIN")
                try:
                    print("GETTING_SYSID")
                    uav_id, mode, lat, lon, heading, alti, packet_counter = self.get_encoded_telemetry()
                    break
                except Exception as err:
                    print("TRYING AGAIN", err)

        swarm_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        swarm_recv_sock.bind((self.local_bind_ip, self.swarmrecv_port))
        swarm_recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.recv_dt = {}
        swarmrecv_thrd = threading.Thread(target=self.recv_from_swarmcontroller, args=[swarm_recv_sock])
        swarmrecv_thrd.start()

        temp = {"SYSID": 0,"MODE": "", "GEOLOCATION": [], "HUMANS": [], "G": 0.0, "P": 0.0, "BESTLOC": (0, 0), "GBESTLOC": (0, 0),"PAYLOAD": 0, "DROPLOCATION": (0, 0), "PD": (0, 0), "PACKETNO": 0, "SENDTIME": 0.0,"RECVTIME": 0.0}
        uav_id, mode, lat, lon, heading, alti, packet_counter = self.get_encoded_telemetry()  # just to get uav id
        modes = ["LAND", "RTL"]
        try:
            uav_id, mode, lat, lon, heading, alti, packet_counter = self.get_encoded_telemetry()
        except Exception as err:
            print("error in getting uav_id", err)
        while True:
            shared_dt = dt["DICT"]
            try:
                """
                if shared_dt == {} and was_filled == 1:
                    print("DICT_EMPTY")
                    print(">>>>>>>>>>>>>>>>LAND>>>>>>>>>>>>>>>>>>>>>>")
                    self.vehicle.mode = VehicleMode("LAND")
                    self.vehicle.flush()
                    time.sleep(self.sleep_time)
                """
                uav_id, mode, lat, lon, heading, alti, packet_counter = self.get_encoded_telemetry()  # from gps_package
                if shared_dt == {}:
                    temp["SYSID"] = uav_id
                    temp["MODE"] = mode
                    temp["GEOLOCATION"] = [lat, lon, heading, alti]
                    temp["PACKETNO"] = packet_counter
                    temp["SENDTIME"] = time.time()
                    temp["RECVTIME"] = 0.0
                    shared_dt[uav_id] = temp

            except Exception as err:
                print("error in encoded_telemtry", err)
                continue

            try:
                # order is very imp
                temp["SYSID"] = uav_id
                temp["MODE"] = mode
                temp["GEOLOCATION"] = [lat, lon, heading, alti]
                temp["PACKETNO"] = packet_counter
                temp["SENDTIME"] = time.time()
                temp["RECVTIME"] = 0.0

                print("TESTING RECV_DT", self.recv_dt)
                # recv_dt = self.recv_from_swarmcontroller(swarm_recv_sock, temp)  # update only g ,b best loc
                if self.recv_dt != {}:
                    temp["HUMANS"] = self.recv_dt["HUMANS"]
                    print("RECV_DT", self.recv_dt)
                    # shared_dict["DICT"] = temp
                    temp["G"] = self.recv_dt["G"]
                    temp["P"] = self.recv_dt["P"]
                    temp["BESTLOC"] = self.recv_dt["BESTLOC"]
                    temp["GBESTLOC"] = self.recv_dt["GBESTLOC"]
                    temp["PAYLOAD"] = self.recv_dt["PAYLOAD"]
                    temp["DROPLOCATION"] = self.recv_dt["DROPLOCATION"]
                    temp["PD"] = self.recv_dt["PD"]

            except Exception as err:
                print("error in assigment in recv_data", err)
            shared_dt[uav_id] = temp
            try:
                temp = shared_dt[int(uav_id)]
                if temp is None or temp == {}:
                    continue
                else:
                    try:
                        app_json = json.dumps(temp).encode("UTF-8")
                        self.send_sock.sendto(app_json, (self.multicast_addr, self.port))
                        # print("...............SENT MESSAGE TO OTHER UAVS............")
                    except Exception as err:
                        self.send_sock.close()
                        self.send_sock = self.create_sender_socket()
            except Exception as err:
                print("Error in Send Intel ", err)

            time.sleep(self.sleep_time)

    def send_to_swarmcontroller(self, sock, dt):
        try:
            app_json = json.dumps(dt, sort_keys=True).encode("UTF-8")
            sock.sendto(app_json, (self.swarm_send_ip, self.swarm_send_port))
            # print("Data sent to swarm_code")
        except Exception as err:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("Error in send to swarmcontroller", err)

    def recv_from_swarmcontroller(self, sock):
        sock.settimeout(1)
        while True:
            try:
                bin_str = sock.recv(2048)
                dt = json.loads(bin_str.decode('utf-8'))
                print(".....DATA_RECEIVED FROM SWARM..........")
                self.recv_dt = dt

            except Exception as err:
                print("No Data Received from swarm_code " + str(err))

    def clear_shared_list(self, dt, threshlod_time, was_filled):
        while True:
            shared_dt = dt["DICT"]
            arr = set(dt["NEW_UAV"])
            if shared_dt is None or shared_dt == {}:
                time.sleep(1)
                continue
            try:
                was_filled.value = 1
                for key, data in shared_dt.items():
                    if time.time() - data["RECVTIME"] < threshlod_time:
                        shared_dt[key] = data
                    else:
                        if int(key) in arr:
                            arr.remove(int(key))
                # print("Clearing DICT",arr)
            except Exception as err:
                print("Error in clearing list ", err)
            dt["DICT"] = shared_dt
            dt["NEW_UAV"] = arr
            time.sleep(self.sleep_time)

    def main_thread(self):
        # Create WiFi Adhoc Multicast
        self.send_sock = self.create_sender_socket()
        if self.send_sock is None:
            self.send_sock = self.create_sender_socket()

        self.recv_sock = self.create_and_bind_receiver_socket(self.multicast_addr, self.port)
        self.recv_sock.settimeout(0.1)

        if self.recv_sock is None:
            self.recv_sock = self.create_and_bind_receiver_socket(self.multicast_addr, self.port)
            self.recv_sock.settimeout(0.1)

        with multiprocessing.Manager() as manager:

            shared_dict = manager.dict({"DICT": {}, "STATIC_DICT": {}, "NEW_UAV": []})
            self.was_filled = multiprocessing.Value("i", 0)

            send_process = multiprocessing.Process(target=self.send_packets, args=[shared_dict, self.was_filled])
            recv_process = multiprocessing.Process(target=self.recv_packets, args=[shared_dict])

            send_process.start()
            recv_process.start()
            
            clear_thread = threading.Thread(target=self.clear_shared_list, args=(shared_dict, self.refresh_rate, self.was_filled))
            clear_thread.start()

            swarm_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while True:
                temp = shared_dict["DICT"].copy()
                print("######...MAIN...#####", [key for key in sorted(temp.keys())])
                [print(key, " :: ", temp[key]) for key in sorted(temp.keys())]
                self.logger.info(str(temp) + "\n")
                self.send_to_swarmcontroller(swarm_send_sock, temp)
                time.sleep(.1)


if __name__ == "__main__":

    try:
        path = sys.argv[1]
        sysid = int(sys.argv[2])
        #path = sys.argv[1]
        #system_id=int(sys.argv[2])
        os.chdir(path)
        multicast(sysid)
    except Exception as err:
        sysid = 0
        print("SYSID NOT GIVEN")
        print("Error Thrown", err)
