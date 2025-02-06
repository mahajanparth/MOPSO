import os

from dronekit import connect, Command, LocationGlobal
import time
import math
import datetime

class Correct_Gps(object):
    def __init__(self,addr='127.0.0.1',port="14553"):
        
        self.addr=addr
        self.port=port
        self.cent_lon = 0
        self.cent_lat = 0
        self.alti = 0
        self.bear = 0
        self.file_hd=open("gps_log.txt","w")
        self.log=open("logs/"+str(datetime.datetime.now())+".txt","w")

        try:
            self.vehicle = connect(addr +':'+port)
        except Exception as err:
            print("ERROR connecting to vehicle",err)
        
    """
    def rad_to_degrees(rad):
        totalSeconds = (rad * 360 * 60 * 60) / (2 * math.pi)
        seconds = totalSeconds % 60
        minutes = (totalSeconds / 60) % 60
        degrees = (totalSeconds / (60 * 60) ) %180
        return int(degrees) ,int(minutes) ,int(seconds)
    """

    def tag_attitude(self):
        try:

            self.cent_lon = self.vehicle.location.global_frame.lon  # frame type can be changed
            self.cent_lat = self.vehicle.location.global_frame.lat
            self.alti = (self.vehicle.location.global_frame.alt) * (-1)
            self.bear=   self.vehicle.heading
        except:
            print("sleeping for 1 sec")
            time.sleep(1)
            self.vehicle = connect(self.addr + ':' + self.port)
        
        return self.cent_lat,self.cent_lon,self.alti,self.bear
    def save_gps(self,li1,li2):
        #li1=[lon,lat,alt,bear]

        lon = (li1[1] + li2[1] ) /2
        lat = (li1[0]+li2[0] ) /2
        alti = (li1[2] + li2[2] ) /2
        bear=(li1[3] + li2[3] ) /2

        param=str(datetime.datetime.now())+" "+str(lon)+" "+str(lat)+" "+str(alti)+" "+str(bear)+"\n"
        self.file_hd.write(param)
        self.log.write(param)
        #print("IN GPS CORRECTION ",lat,lon,alti,bear)
        return [lat,lon,alti,bear]

    def file_close(self):
        self.file_hd.close()
        self.log.close()

if __name__ == '__main__':
    #main()
    pass