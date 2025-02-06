import multiprocessing as mp
import socket
import sys
import os
try:
    path=sys.argv[1]
    sysid=sys.argv[2]
    os.chdir(path)
    print(os.getcwd(),sys.argv[1])
except:
    sysid=0
    path="/home/uas-dtu/Desktop/new_on_uav/VISION"
    os.chdir(path)

from VideoGrabber import videograbber
from VideoStreamer.Server import Server
import human_detection
#from GPS_DENIED.GPS_DENIED import gps_denied

class Planner:
    def __init__(self):


        _camera=videograbber().start()
        _camera.stop_camera=False

        obj = human_detection.inference()
        video_source = -1
        self.local_bind_ip="127.0.0.1"
        self.swarmrecv_port=10005

        self.vision_event = mp.Event()
        self.vision_process=mp.Process(target=obj.runOnVideo,args=(_camera.array,self.vision_event,video_source,_camera.shape,path,None,None))
        print("CLASSIFIER STARTED")
        #self.gpsdenied_event = mp.Event()
        #self.gpsdenied_process = mp.Process(target=gps_denied().main, args=(self.gpsdenied_event, _camera.array,_camera.shape))

        print("SERVER STARTED")
        self.videotransmit_event = mp.Event()
        self.videotransmit_process = mp.Process(target=Server().main, args=(self.videotransmit_event, _camera.array,_camera.shape,sysid))

        #print("hello3")
        #self.search_event = mp.Event()
        #self.search_process = mp.Process(target=, args=(self.search_event, _camera.array, _camera.shape))

        self.process_maintainer()

        
    def process_maintainer(self):
        self.videotransmit_process.start()
        self.vision_event.clear()
        self.vision_process.start()
        #self.gpsdenied_process.start()
        swarm_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        swarm_recv_sock.bind((self.local_bind_ip, self.swarmrecv_port))
        swarm_recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        swarm_recv_sock.settimeout(1)
        print("Waiting For Data")
        while True:

            try:

                message = swarm_recv_sock.recv(128)
                message=message.decode("UTF-8")

                #dt = json.loads(bin_str.decode('utf-8'))
                print(".........DATA_RECEIVED FROM SWARM..........")
                if message == "START":
                    print("............VISION STARTED...............")
                    self.vision_event.set()
                if message == "STOP":
                    self.vision_event.clear()
                    print("............VISION STOPPED...............")

            except Exception as err:
                #print("No Data Received from swarm_code " + str(err))
                pass




if __name__=="__main__":
    Planner()