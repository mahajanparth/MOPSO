import cv2
import time
import multiprocessing as mp
import threading
import numpy as np
import dronekit as dk
import socket
import json

class gps_denied:
    def __init__(self ):
        # write code to synchronize gps lat long with viedo frames
        #self.camera_obj=cv2.VideoCapture(-1)
        #self.camera_obj.set(3,1980)
        #self.camera_obj.set(4,1440)
        #self.camera_obj.set(5, 10)
        self.frame=None
        self.stop_camera=False

        #height=int(self.camera_obj.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #width=int(self.camera_obj.get(cv2.CAP_PROP_FRAME_WIDTH))
        #self.shape=(height,width,3)

        self.local_bind_ip="127.0.0.1"
        self.recv_port=11000
        #self.server_send_ip="127.0.0.1"
        #self.server_send_port=11001

        self_connection_string="127.0.0.1:14552"
        #self.array = mp.RawArray('d', int(height) *int( width)* 3)
        #self.np_array = np.frombuffer(self.array, dtype=np.float64).reshape((int(height),int(width),3))
        self.packet_counter=0
        self.visual_odometry_gps=[0,0]
        self.gps_state=True

        try:
            self.server_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # swarm_send_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

            self.server_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_recv_sock.bind((self.local_bind_ip, self.recv_port))
            self.server_recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as err:
            print("Error",err )

        try:
            self.vehicle=dk.connect(self_connection_string)
            print("CONNECTED TO VEHICLE",self_connection_string)
        except Exception as err:
            print("Error",err)
    def dronekit_params(self):

        if self.vehicle is not None:
            try:

                lat = self.vehicle.location.global_frame.lat
                lon = self.vehicle.location.global_frame.lon
                alti = self.vehicle.location.global_relative_frame.alt
                heading = self.vehicle.heading
                # print(vehicle.parameters["SYSID_THISMAV"])
                uav_id = int(self.vehicle.parameters['SYSID_THISMAV'])
                mode=self.vehicle.mode.name
                message = [uav_id,mode, lat, lon, heading, alti]
                print("GPS_DENIED",message)
                return message
            except Exception as err:
                print("ERROR IN DRONEKIT PARAMS",err)
        else:
            return None

    def send_to_server(self, dict,address):

        try:

            app_json = json.dumps(dict).encode("UTF-8")
            self.server_send_sock.sendto(app_json, (address))
            print("Data sent to server")


        except Exception as err:
            self.server_send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("ERROR IN SENDING", err)

    def get_GPS_state(self):
        return self.gps_state
    def change_GPS_state(self,state):
        self.gps_state=state

    def array_to_npimage(self,array,shape):
        frame=np.frombuffer(array, dtype=np.float64).reshape(shape)
        return frame.astype("uint8")


    def visual_odometry(self,event,array,shape):  # replace visual odometry code
        print("VISUAL_ODOMETRY_STARTED")
        while True:

            if event.is_set():
                print("VISUAL ODOMETRY",event.is_set())
                event.wait()
            else:
                try:
                    frame=self.array_to_npimage(array,shape)
                    cv2.imshow("VISUAL_ODOMETRY",frame)
                    if cv2.waitKey(10)==ord('q'):
                        break


                except Exception as err:
                    print("EXCEPTION AS ERR",err)
                    pass

    def main(self,event,array,shape):
        #recv_thread=threading.Thread(target=self.recv_from_server)
        visual_odometry_thread=threading.Thread(target=self.visual_odometry,args=[event,array,shape])
        visual_odometry_thread.daemon=True

        #recv_thread.start()
        visual_odometry_thread.start()

        #self.server_recv_sock.settimeout(0.1)

        while True:

            try:
                print("GPS_DENIED")
                message, address = self.server_recv_sock.recvfrom(128)
                print("GPS_DENIED",message)
                message = message.decode("utf-8")
                print("..........GPS_DENIED.................", message)
                if message == "GPS":
                    arr=self.dronekit_params()
                    if arr ==None:

                        continue
                    else:
                        uav_id, mode, lat, lon, heading, alti = arr
                    print("........YOYO_GPS..........",arr)
                    if self.get_GPS_state():
                        print("YOYO_GPS1")
                        data = {"message": [uav_id, lat, lon, heading, alti, self.packet_counter]}
                        if data == None:
                            continue
                        print("YOYO_GPS2")
                        self.packet_counter += 1
                        self.send_to_server(data, address)
                    else:
                        lat, long = self.visual_odometry_gps
                        data = {"message": [uav_id, lat, lon, heading, alti, self.packet_counter]}

                        if data == None:
                            continue
                        self.packet_counter += 1
                        self.send_to_server(data, address)

                elif message == "STATE":
                    data = {"message": [str(self.vehicle.mode.name)]}
                    self.send_to_server(data, address)


            except Exception as err:
                print("exception occurred in recv_data " + str(err))
                time.sleep(.1)
                continue



if __name__=="__main__":
    pass