from ctypes import *
import random
import cv2
import numpy as np
from gps_correction import Correct_Gps
from calc_gps import gps
import os
import time
import logging
from dronekit import mavutil , connect
import sys
import socket
import json
try:
    path=sys.argv[1]
    os.chdir(path)
except:
    pass

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

    


class IplROI(Structure):
    pass

class IplTileInfo(Structure):
    pass

class IplImage(Structure):
    pass

IplImage._fields_ = [
    ('nSize', c_int),
    ('ID', c_int),
    ('nChannels', c_int),               
    ('alphaChannel', c_int),
    ('depth', c_int),
    ('colorModel', c_char * 4),
    ('channelSeq', c_char * 4),
    ('dataOrder', c_int),
    ('origin', c_int),
    ('align', c_int),
    ('width', c_int),
    ('height', c_int),
    ('roi', POINTER(IplROI)),
    ('maskROI', POINTER(IplImage)),
    ('imageId', c_void_p),
    ('tileInfo', POINTER(IplTileInfo)),
    ('imageSize', c_int),          
    ('imageData', c_char_p),
    ('widthStep', c_int),
    ('BorderMode', c_int * 4),
    ('BorderConst', c_int * 4),
    ('imageDataOrigin', c_char_p)]


class iplimage_t(Structure):
    _fields_ = [('ob_refcnt', c_ssize_t),
                ('ob_type',  py_object),
                ('a', POINTER(IplImage)),
                ('data', py_object),
                ('offset', c_size_t)]

class inference(object):

    #lib = CDLL("./darknet/libdarknet.so", RTLD_GLOBAL)
    path=os.getcwd()
    print(path)
    #lib = CDLL(path+"/"+"darknet/libdarknet.so", RTLD_GLOBAL)
    lib = CDLL(path+"/darknet/libdarknet.so", RTLD_GLOBAL)
    lib.network_width.argtypes = [c_void_p]
    lib.network_width.restype = c_int
    lib.network_height.argtypes = [c_void_p]
    lib.network_height.restype = c_int

    predict = lib.network_predict
    predict.argtypes = [c_void_p, POINTER(c_float)]
    predict.restype = POINTER(c_float)

    set_gpu = lib.cuda_set_device
    set_gpu.argtypes = [c_int]

    make_image = lib.make_image
    make_image.argtypes = [c_int, c_int, c_int]
    make_image.restype = IMAGE

    get_network_boxes = lib.get_network_boxes
    get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
    get_network_boxes.restype = POINTER(DETECTION)

    make_network_boxes = lib.make_network_boxes
    make_network_boxes.argtypes = [c_void_p]
    make_network_boxes.restype = POINTER(DETECTION)

    free_detections = lib.free_detections
    free_detections.argtypes = [POINTER(DETECTION), c_int]

    free_ptrs = lib.free_ptrs
    free_ptrs.argtypes = [POINTER(c_void_p), c_int]

    network_predict = lib.network_predict
    network_predict.argtypes = [c_void_p, POINTER(c_float)]

    reset_rnn = lib.reset_rnn
    reset_rnn.argtypes = [c_void_p]

    load_net = lib.load_network
    load_net.argtypes = [c_char_p, c_char_p, c_int]
    load_net.restype = c_void_p

    do_nms_obj = lib.do_nms_obj
    do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

    do_nms_sort = lib.do_nms_sort
    do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

    free_image = lib.free_image
    free_image.argtypes = [IMAGE]

    letterbox_image = lib.letterbox_image
    letterbox_image.argtypes = [IMAGE, c_int, c_int]
    letterbox_image.restype = IMAGE

    load_meta = lib.get_metadata
    lib.get_metadata.argtypes = [c_char_p]
    lib.get_metadata.restype = METADATA

    load_image = lib.load_image_color
    load_image.argtypes = [c_char_p, c_int, c_int]
    load_image.restype = IMAGE

    rgbgr_image = lib.rgbgr_image
    rgbgr_image.argtypes = [IMAGE]

    predict_image = lib.network_predict_image
    predict_image.argtypes = [c_void_p, IMAGE]
    predict_image.restype = POINTER(c_float)


    def __init__(self):
        pass


    def classify(self,net, meta, im):
        out = inference.predict_image(net, im)
        res = []
        for i in range(meta.classes):
            res.append((meta.names[i], out[i]))
        res = sorted(res, key=lambda x: -x[1])
        return res


    def array_to_image(self,arr):
        # need to return old values to avoid python freeing memory
        arr = arr.transpose(2,0,1)
        c, h, w = arr.shape[0:3]
        arr = np.ascontiguousarray(arr.flat, dtype=np.float32) / 255.0
        data = arr.ctypes.data_as(POINTER(c_float))
        im = IMAGE(w,h,c,data)
        return im, arr

    def detect(self,net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
        """if isinstance(image, bytes):
            # image is a filename
            # i.e. image = b'/darknet/data/dog.jpg'
            im = load_image(image, 0, 0)
        else:
            # image is an nparray
            # i.e. image = cv2.imread('/darknet/data/dog.jpg')
            im, image = array_to_image(image)
            rgbgr_image(im)
        """
        im, image = self.array_to_image(image)
        inference.rgbgr_image(im)
        num = c_int(0)
        pnum = pointer(num)
        inference.predict_image(net, im)
        dets = inference.get_network_boxes(net, im.w, im.h, thresh,hier_thresh, None, 0, pnum)
        num = pnum[0]
        if nms: inference.do_nms_obj(dets, num, meta.classes, nms)

        res = []
        for j in range( num ):
            a = dets[j].prob[0:meta.classes]
            if any(a):
                ai = np.array(a).nonzero()[0]
                for i in ai:
                    b = dets[j].bbox
                    res.append((meta.names[i], dets[j].prob[i],
                               (b.x, b.y, b.w, b.h)))

        res = sorted(res, key=lambda x: -x[1])
        if isinstance(image, bytes): inference.free_image(im)
        inference.free_detections(dets, num)
        return res

    def send_to_modified_server(self, sock, dt):

        try:

            app_json = json.dumps(dt).encode("UTF-8")
            sock.sendto(app_json, ("127.0.0.1", 10002))
            print("Data sent to swarm_code")


        except Exception as err:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("Error in send to swarmcontroller", err)

    def set_servo(self,vehicle, servo_number, pwm_value):
        pwm_value_int = int(pwm_value)
        msg = vehicle.message_factory.command_long_encode(
            0, 0,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            servo_number,
            pwm_value_int,
            0, 0, 0, 0, 0
        )
        for i in range(5):
            vehicle.send_mavlink(msg)
        print("..................DROPPED_PAYLOAD..........................")


    def frame_to_npimage(self,array,shape):
        frame=np.frombuffer(array, dtype=np.float64).reshape(shape)
        return frame.astype("uint8")

    def runOnVideo(self,array,event,vid_source,shape,path,net, meta,  thresh=.3, hier_thresh=.5, nms=.45):
        print(os.getcwd())
        logging.basicConfig(filename="human_detection.log", format="%(module)s %(lineno)d %(message)s", filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        cfg_path=path+"/darknet/files/tiny_human_detection.cfg"
        weight_path=path+"/darknet/backup/tiny_human_detection_125000.weights"
        data_path=path+"/darknet/files/human.data"
        #net = inference.load_net(b"./darknet/cfg/yolov3-tiny.cfg", b"./darknet/yolov3-tiny.weights", 0)
        #meta = inference.load_meta(b"./darknet/cfg/coco.data")
        net = self.load_net(cfg_path.encode(),weight_path.encode(),0)
        meta = self.load_meta(data_path.encode())#(b"/home/uas-dtu/Desktop/new_on_uav/VISION/darknet/files/human.data")
        payload_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        local_ip="127.0.0.1"
        payload_port=20000

        #video = cv2.VideoCapture(vid_source)
        count = 0
        human_list=[]
        gps_obj=Correct_Gps(addr="127.0.0.1",port="14553")
        save_gps=gps()
        classes_box_colors = [(0, 0, 255), (0, 255, 0)]  #red for palmup --> stop, green for thumbsup --> go
        classes_font_colors = [(255, 255, 0), (0, 255, 255)]
        cent_lat,cent_lon,alti,bear=[0,0,0,0]


        while True:
            if not event.is_set():
                print("......................waiting to be set again.............................................")
                event.wait()
                #pause the run on video
            start = time.time()

            try:

                li1=gps_obj.tag_attitude()
                frame=self.frame_to_npimage(array,shape)
                print("......................waiting to be cleared.............................................",event.is_set())
                #res, frame = video.read()
                li2=gps_obj.tag_attitude()
                cent_lat,cent_lon,alti,bear=gps_obj.save_gps(li1,li2)
            except Exception as err:
                print("error in runOnVideo",err)
                self.logger.debug(err)
                continue


            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im, arr = self.array_to_image(rgb_frame)

            #cv2.imshow("frame",frame)
            #if cv2.waitKey(10)==ord("q"):
            #    break

            num = c_int(0)
            pnum = pointer(num)
            inference.predict_image(net, im)

            dets = inference.get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
            num = pnum[0]

            if (nms): inference.do_nms_obj(dets, num, meta.classes, nms);
            # res = []
            font = cv2.FONT_HERSHEY_SIMPLEX
            print(count)
            for j in range(num):
                for i in range(meta.classes):
                    if dets[j].prob[i] > 0:
                        try:

                            b = dets[j].bbox
                            x1 = int(b.x - b.w / 2.)
                            y1 = int(b.y - b.h / 2.)
                            x2 = int(b.x + b.w / 2.)
                            y2 = int(b.y + b.h / 2.)
                            #cv2.rectangle(frame, (x1, y1), (x2, y2), classes_box_colors[i], 2)
                            #print(meta.names[i],meta.names[i])
                            #cv2.putText(frame, str(meta.names[i]), (x1, y1 - 20), 2, font, classes_font_colors[i], 5, cv2.LINE_AA)
                            #cv2.putText(frame, str(meta.names[i]), (x1, y1 - 20), font,1, classes_font_colors[i], 1, cv2.LINE_AA)

                            try:

                                if  meta.names[i] == b'HUMAN':
                                    #humans_list.append([lat,lon])
                                    print("In classifier",bear,alti,cent_lat,cent_lon,frame.shape)
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), classes_box_colors[i], 2)
                                    #print(meta.names[i],meta.names[i])
                                    #cv2.putText(frame, str(meta.names[i]), (x1, y1 - 20), 2, font, classes_font_colors[i], 5, cv2.LINE_AA)
                                    cv2.putText(frame, str(meta.names[i]), (x1, y1 - 20), font,1, classes_font_colors[i], 1, cv2.LINE_AA)

                                    lat,lon=save_gps.compute_gps( int((x1 + x2)/2),int((y1+y2)/2.0),bear,alti,cent_lat,cent_lon,frame.shape)


                                    cv2.putText(frame, str(lat)+" "+str(lon), (x1, y1 + 20), font,1, classes_font_colors[i], 1, cv2.LINE_AA)

                                    print("lat,long")
                                    print(lat,lon)
                                    name = path+"/save/" + str(lat) + " " + str(lon) + ".jpg"
                                    cv2.imwrite(name, frame)
                                    print("lat ", "lon ", lat, lon)
                                    self.logger.info(str(lat) + " " + str(lon))
                                    message="PAYLOAD"
                                    """            elif event == "PAYLOAD":
                                    print("Sending PAYLOAD")
                                    message = "PAYLOAD"
                                    sysid = int(values["UAV_NO"])
                                    L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                                    L_thread.start()

                                    
                                    """
                                    dt={}
                                    dt["MESSAGE"]="DROP"
                                    dt["SYS_ID"]=0
                                    dt["PAYLOAD"]=[]
                                    dt["PACKET_NO"]=0
                                    dt["TIMESTAMP"]=0

                                    #payload_sock.sendto(message.encode("utf-8"), (local_ip, payload_port))
                                    app_json = json.dumps(dt).encode("UTF-8")
                                    payload_sock.sendto(app_json, (local_ip, payload_port))

                                    print("____________DROPPING PAYLOAD____________")
                                    self.logger.info("____________DROPPING PAYLOAD____________")
                                    dt={}
                                    dt["HUMANS"]=[lat,lon,1,0]
                                    self.send_to_modified_server(payload_sock,dt)
                                    print(lat, lon)
                                    # self.drop_waypoint()

                                    #self.drop_waypoint()


                                    #write_str=str(str(lat)+" " +str(lon)+"\n")
                                    #self.signs_txt.write(write_str)
                                    #self.signs_txt.flush()


                                #add the lat long to a dict with different classes and list of gps coordinates
                            except Exception as err:
                                self.logger.debug(err)
                                print("error in RUNONVIDEO",err)

                        except Exception as err:
                            self.logger.debug(err)
                            print("Rect_not_printed",err)
            #cv2.imshow('Human_Detection', frame)
            print(1/(time.time()-start))
            #if cv2.waitKey(1) == ord('q'):
            #    break
            # print res
            count += 1


if __name__ == "__main__":
    obj=inference()
    video_source = -1
    obj.runOnVideo2(video_source,obj.net, obj.meta)
    #obj.runOnVideo(None, None, video_source)


    #runOnVideo(net, meta, vid_source)
