import cv2
import time
import multiprocessing as mp
import threading
import numpy as np
import glob
import socket
import json

class videograbber:
    def __init__(self  ):
        # write code to synchronize gps lat long with viedo frames
        self.camera_obj=cv2.VideoCapture(-1)
        self.camera_obj.set(3,1280)
        self.camera_obj.set(4,920)
        #self.camera_obj.set(5, 10)
        self.frame=None
        self.stop_camera=False

        height=int(self.camera_obj.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width=int(self.camera_obj.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.shape=(height,width,3)
        self.array = mp.RawArray('d', int(height) *int( width)* 3)
        self.np_array = np.frombuffer(self.array, dtype=np.float64).reshape((int(height),int(width),3))

        self.prev_ret_code=True
        self.local_ip="127.0.0.1"
        self.local_server_port=20000



    def start(self):
        threading.Thread(target=self.read_frames).start()
        return self
    def read_frames(self):

        self.prev_ret_code = True
        local_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_dt = {}
        temp_dt["MESSAGE"] = "CAMERA_CONNECTED"
        temp_dt["SYS_ID"] = 0
        temp_dt["PAYLOAD"] = []
        temp_dt["PACKET_NO"] = 0
        temp_dt["TIMESTAMP"] = 0
        app_json = json.dumps(temp_dt).encode("UTF-8")
        local_sock.sendto(app_json, (self.local_ip, self.local_server_port))

        while True:
            if not self.stop_camera:
                #print("Camera_working")
                start = time.time()
                ret_code, self.frame = self.camera_obj.read()

                if ret_code != self.prev_ret_code:
                    self.prev_ret_code = ret_code
                    if ret_code:
                        temp_dt = {}
                        temp_dt["MESSAGE"] = "CAMERA_CONNECTED"
                        temp_dt["SYS_ID"] = 0
                        temp_dt["PAYLOAD"] = []
                        temp_dt["PACKET_NO"] = 0
                        temp_dt["TIMESTAMP"] = 0
                        app_json = json.dumps(temp_dt).encode("UTF-8")
                        local_sock.sendto(app_json, (self.local_ip, self.local_server_port))
                    else:
                        temp_dt = {}
                        temp_dt["MESSAGE"] = "CAMERA_DISCONNECTED"
                        temp_dt["SYS_ID"] = 0
                        temp_dt["PAYLOAD"] = []
                        temp_dt["PACKET_NO"] = 0
                        temp_dt["TIMESTAMP"] = 0
                        app_json = json.dumps(temp_dt).encode("UTF-8")
                        local_sock.sendto(app_json, (self.local_ip, self.local_server_port))

                if ret_code:
                    np.copyto(self.np_array, self.frame)
                    end = time.time()
                else:
                    print("Releasing Camera")
                    self.camera_obj.release()
                    time.sleep(5)

                    try:
                        cam_list=glob.glob("/dev/video*")
                        for cam in cam_list:
                            print("Connecting_cam",cam)
                            self.camera_obj = cv2.VideoCapture(cam)
                            self.camera_obj.set(3,1280)
                            self.camera_obj.set(4,920)
                            time.sleep(5)
                            print("Path")

                    except Exception as err :
                        print("Waiting for camera",err)
                # wait for event to be True

            else:
                print("Killing the camera ")
                break



    def release_camera(self):
        try:
            self.camera_obj.release()
        except:
            print("Error in Releasing camera",err)

if __name__=="__main__":
    obj=videograbber().start()

    while True:
        try:
            frame=obj.frame
            print(obj.frame.shape)

            cv2.imshow("Video_Grabber",frame)

            if cv2.waitKey(10)==ord("q"):
                break

        except Exception as err:
            print(err)

    obj.release_camera()
