import os
import subprocess
import socket
import pickle
import paramiko
import threading
import PySimpleGUI as sg
import json
# from dronekit import connect
from GUI import graphic
import time
from datetime import datetime

global graphic_object
graphic_object = graphic()

global params

def Set_Ad_hoc_func():
    subprocess.call("bash set_adhoc_gcs.sh", shell=True)


def Disable_Ad_hoc_func():
    subprocess.check_call("bash revert_adhoc_gcs.sh", shell=True)


def Test_connections_func():
    Num_of_UAVs = params[0]
    UAV_list = list(range(211, 211 + Num_of_UAVs))
    Connection_list = list()

    while (len(UAV_list) != 0):
        for i in UAV_list:
            server_ip = "192.168.4.{0}".format(i)
            result = os.system('ping -c 1 ' + server_ip)

            if result == 0:
                print("connected to UAV ", (i % 10))
                UAV_list.remove(i)
                Connection_list.append(i)
        print(Connection_list)


def Plan_mission_func(place):
    # os.chdir("/home/parth/ardupilot/ArduCopter")
    print("gnome-terminal -- sim_vehicle.py -v ArduCopter -L " + place + " --map &")
    subprocess.check_call("gnome-terminal -- sim_vehicle.py -v ArduCopter -L"+place+" --map &", shell=True)
"""

def Save_wp_func():
    vehicle = connect('127.0.0.1:14550')

    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    waypoint_list = list()

    for cmd in cmds:
        waypoint_list.append([cmd.x, cmd.y])

    dump_wp_file = open("wp_list", "wb")
    pickle.dump(waypoint_list, dump_wp_file)
    dump_wp_file.close()
    print("waypoint saved to waypoint_list")
    print(waypoint_list)
"""

def map():
    # attach joy code here
    pass

def video_start_client(serverAddr,serverPort,rtpPort,fileName="Webcam"):
    global stream_list
    if serverAddr not in stream_list:

        try:
            print(os.getcwd())
            command="gnome-terminal -- python3 "+os.getcwd()+"/VIDEO_STREAMER/ClientLauncher.py " +str(serverAddr)+" "+str(serverPort)+" "+str(rtpPort)+" "+str(fileName)
            subprocess.check_call(command,shell=True)
            stream_list.append(serverAddr)
        except Exception as err:
            print("Exception in video_start_client",err)
            return 1
    else:
        print("Client Already Running", serverAddr,serverPort,rtp_port)
        print(stream_list)
        return 0

def send_to_uav(message, sysid,mode=1,payload=False):
    global uav_dict
    global sock
    global packet_num
    print(message, sysid)
    packet_num += 1
    dt={ "TIMESTAMP":time.time(),"PACKET_NO": packet_num}

    if mode==0:
        message="P2P_"+message
        if sysid == -1:
            for key in uav_dict["INTEL"].keys():
                try:
                    ip = uav_dict["INTEL"][key][0]
                    port = 20000
                    dt["MESSAGE"] = message
                    dt["SYS_ID"] = int(key)
                    if payload :
                        dt["PAYLOAD"]=payload
                    else:
                        dt["PAYLOAD"] = []
                    app_json = json.dumps(dt).encode("UTF-8")
                    sock.sendto(app_json, (ip, port))


                except Exception as err:
                    print(err)

            for key in uav_dict["DTC"].keys():
                try:
                    ip = uav_dict["DTC"][key][0]
                    port = 20000
                    dt["MESSAGE"] = message
                    dt["SYS_ID"] = int(key)
                    if payload:
                        dt["PAYLOAD"] = payload
                    else:
                        dt["PAYLOAD"] = []

                    app_json = json.dumps(dt).encode("UTF-8")
                    sock.sendto(app_json, (ip, port))


                except Exception as err:
                    print(err)


        elif sysid in uav_dict["INTEL"].keys() and sysid in uav_dict["DTC"].keys() :
            try:

                ip = uav_dict["INTEL"][sysid][0]
                port = 20000
                dt["MESSAGE"] = message
                dt["SYS_ID"] = int(sysid)
                if payload:
                    dt["PAYLOAD"] = payload
                else:
                    dt["PAYLOAD"] = []

                app_json = json.dumps(dt).encode("UTF-8")
                sock.sendto(app_json, (ip, port))
                print(ip, port)

            except Exception as err:
                print(err)

            try:

                ip = uav_dict["DTC"][sysid][0]
                port = 20000
                dt["MESSAGE"] = message
                dt["SYS_ID"] = int(sysid)
                if payload:
                    dt["PAYLOAD"] = payload
                else:
                    dt["PAYLOAD"] = []

                app_json = json.dumps(dt).encode("UTF-8")
                sock.sendto(app_json, (ip, port))
                print(ip, port)
            except Exception as err:
                print(err)

        elif sysid in uav_dict["INTEL"].keys():
            try:

                ip = uav_dict["INTEL"][sysid][0]
                port = 20000
                dt["MESSAGE"] = message
                dt["SYS_ID"] = int(sysid)

                if payload:
                    dt["PAYLOAD"] = payload
                else:
                    dt["PAYLOAD"] = []

                app_json = json.dumps(dt).encode("UTF-8")
                sock.sendto(app_json, (ip, port))
                print(ip, port)

            except Exception as err:
                print(err)

        #print("SENT", uav_dict.keys())
        #print(dt)


    elif mode ==1:
        message = "ROUTING_" + message
        if sysid == -1:

            for key in uav_dict["DTC"].keys():
                try:
                    ip = uav_dict["DTC"][key][0]
                    port = 20000
                    for id in uav_dict["INTEL"].keys():

                        dt["SYS_ID"] = int(id)
                        dt["MESSAGE"] = message
                        if payload:
                            dt["PAYLOAD"] = payload
                        else:
                            dt["PAYLOAD"] = []

                        app_json = json.dumps(dt).encode("UTF-8")
                        sock.sendto(app_json, (ip, port))
                except Exception as err:
                    print(err)


        elif sysid in uav_dict["INTEL"].keys() and sysid in uav_dict["DTC"].keys():
            try:

                ip = uav_dict["DTC"][sysid][0]
                port = 20000
                dt["SYS_ID"] = int(sysid)
                dt["MESSAGE"] = message
                if payload:
                    dt["PAYLOAD"] = payload
                else:
                    dt["PAYLOAD"] = []

                app_json = json.dumps(dt).encode("UTF-8")
                sock.sendto(app_json, (ip, port))
                print(ip, port)
            except Exception as err:
                print(err)

        elif sysid in uav_dict["INTEL"].keys():

            for key in uav_dict["DTC"].keys():
                try:
                    ip = uav_dict["DTC"][key][0]
                    port = 20000
                    dt["MESSAGE"] = message
                    dt["SYS_ID"] = int(sysid)
                    if payload:
                        dt["PAYLOAD"] = payload
                    else:
                        dt["PAYLOAD"] = []

                    app_json = json.dumps(dt).encode("UTF-8")
                    sock.sendto(app_json, (ip, port))
                except Exception as err:
                    print(err)



    elif mode== 2:
        message="BROADCAST_"+message
        if sysid == -1:

            for key in uav_dict["DTC"].keys():
                try:
                    ip = uav_dict["DTC"][key][0]
                    port = 20000
                    for id in uav_dict["INTEL"].keys():

                        dt["SYS_ID"] = int(id)
                        dt["MESSAGE"] = message
                        if payload:
                            dt["PAYLOAD"] = payload
                        else:
                            dt["PAYLOAD"] = []

                        app_json = json.dumps(dt).encode("UTF-8")
                        sock.sendto(app_json, (ip, port))
                except Exception as err:
                    print(err)


        elif sysid in uav_dict["INTEL"].keys() and sysid in uav_dict["DTC"].keys():
            try:

                ip = uav_dict["DTC"][sysid][0]
                port = 20000
                dt["SYS_ID"] = int(sysid)
                dt["MESSAGE"] = message
                if payload:
                    dt["PAYLOAD"] = payload
                else:
                    dt["PAYLOAD"] = []

                app_json = json.dumps(dt).encode("UTF-8")
                sock.sendto(app_json, (ip, port))
                print(ip, port)
            except Exception as err:
                print(err)

        elif sysid in uav_dict["INTEL"].keys():

            for key in uav_dict["DTC"].keys():
                try:
                    ip = uav_dict["DTC"][key][0]
                    port = 20000
                    dt["MESSAGE"] = message
                    dt["SYS_ID"] = int(sysid)
                    if payload:
                        dt["PAYLOAD"] = payload
                    else:
                        dt["PAYLOAD"] = []

                    app_json = json.dumps(dt).encode("UTF-8")
                    sock.sendto(app_json, (ip, port))
                except Exception as err:
                    print(err)
    print("message sent",dt)



def Plan_formation_func():
    weight_matrix,coor_matrix = graphic_object.display()
    print("weight_matrix", weight_matrix)
    dump_weight_matrix_file = open("weight_matrix", "wb")
    pickle.dump(weight_matrix, dump_weight_matrix_file)
    dump_weight_matrix_file.close()
    #parameters["WEIGHT_MAT"] = weight_matrix

    dump_coor_matrix_file = open("coor_matrix", "wb")
    pickle.dump(coor_matrix, dump_coor_matrix_file)
    dump_coor_matrix_file.close()
    parameters["COORDINATES"]=coor_matrix


def upload_mission(ip, password, total_name):
    try:

        command = "sshpass -p " + password + " scp " + total_name + " uas-dtu@" + ip + ":/home/uas-dtu/Desktop/new_on_uav/"
        print(command)
        subprocess.check_call(command, shell=True)
        print("data sent to uav " + ip)
        successful_sent.append(ip)

    except:
        print("data not sent to uav " + ip)
        unsuccessful_sent.append(ip)


def Upload_mission_func():
    password = "Aether"
    # os.chdir("/home/parth/Desktop/new_on_uav/GUI/")
    prog_name = ["number_of_UAVs", "weight_matrix", "wp_list", "uav_list.txt"]
    total_name = ""  #not used right now
    parameter_file = open('number_of_UAVs', 'rb')
    parameters = pickle.load(parameter_file)
    print("Parameters", parameters)
    d_matrix_file = open('weight_matrix', 'rb')
    matrix = pickle.load(d_matrix_file)
    print("MATRIX", matrix)
    wp_file = open("wp_list", 'rb')
    waypoint_list = pickle.load(wp_file)
    print("WAYPOINT_LIST", waypoint_list)
    thread_list = []
    for prog in prog_name:
        total_name += " " + prog

    for ip, port in uav_dict["INTEL"].values():     #uploading mission from intel only
        thrd = threading.Thread(target=upload_mission, args=[ip, password, total_name])
        thread_list.append(thrd)
        thrd.start()
    for thrd in thread_list:
        thrd.join()

    print("successfully_send to ", sorted(successful_sent))
    print("not_successfully_send to ", sorted(unsuccessful_sent))


def target_land_command(key):
    global UAV_INFO
    _, ip, host_name, password, baudrate ,interface= UAV_INFO[key]
    # host_name, password = self.uav_data[ip]_
    OBC_command = "bash /home/" + host_name + "/ssh_land.sh"
    #command = "sshpass -p " + password + " ssh" + " -X " + host_name + "@" + ip + " " + OBC_command
    command = "sshpass -p " + password + " ssh " + host_name + "@" + ip + " " + OBC_command

    try:
        subprocess.check_call(command, shell=True)
        print("Sucessfully copied file to " + host_name + ": " + ip)
        successful_sent.append((host_name, ip))
    except Exception as err:
        print("Error", host_name, ip, err)
        unsuccessful_sent.append((host_name, ip))


def ssh_land():
    thread_list = []
    print(UAV_INFO.keys())
    for key in UAV_INFO.keys():
        thrd = threading.Thread(target=target_land_command, args=[int(key)])
        thread_list.append(thrd)
        thrd.start()

    for thr in thread_list:
        thr.join()
    print("Received error in starting program in some uavs")
    print("successful_uav", successful_sent)
    print("unsuccessful_uav", unsuccessful_sent)


def Kill_map_func():
    subprocess.check_call("killall -9 mavproxy.py")


def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client
def linevisibility_setting(state,line_num):
    i=line_num
    if state=="SHOW":
        temp=True
    else:
        temp = False
    win.Element("COL"+str(i)).Update(visible=temp)
    """
    win.Element('TEXT' + str(i)).Update(visible=temp,)
    win.Element('LAT' + str(i)).Update(visible=temp)
    win.Element('LON' + str(i)).Update(visible=temp)
    win.Element('COMBOBOX' + str(i)).Update(visible=temp)
    win.Element('SPEED' + str(i)).Update(visible=temp)
    """
    win.refresh()


def read_wp_func( waypoint_dict ):
    print("HELLO",waypoint_dict["WAYPOINTS"])
    waypoint_list= waypoint_dict["WAYPOINTS"]
    global line_num
    for i in range(len(waypoint_list)):
        win.Element('LAT' + str(i)).Update(value=str(waypoint_list[i][0]))
        win.Element('LON' + str(i)).Update(value=str(waypoint_list[i][1]))
        win.Element('COMBOBOX' + str(i)).Update(value=["WAYPOINT","MOPSO","FLOCKING"][int(waypoint_list[i][2])])
        win.Element('SPEED' + str(i)).Update(value=str(waypoint_list[i][3]))
        win.Element('ALTITUDE' + str(i)).Update(value=str(waypoint_list[i][4]))
        linevisibility_setting("SHOW", i)
        line_num = i
    line_num += 1  # to prevent two click in show waypoint ,be careful while sending params
    vehicle = None


def load_wp_func():


    vehicle = connect('127.0.0.1:14550')

    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    waypoint_list = list()

    for cmd in cmds:
        waypoint_list.append([cmd.x, cmd.y])



    global line_num
    for i in range(len(waypoint_list)):
        win.Element('LAT' + str(i)).Update(value=str(waypoint_list[i][0]))
        win.Element('LON' + str(i)).Update(value=str(waypoint_list[i][1]))
        linevisibility_setting("SHOW", i)
        line_num = i
    line_num += 1  # to prevent two click in show waypoint ,be careful while sending params
    vehicle = None

def Save_wp_func(values,line_num):
    wp_list=[]
    num=0
    for i in range(line_num):
        if values["COMBOBOX"+str(i)] =="WAYPOINT":
            num=0
        elif values["COMBOBOX"+str(i)] =="MOPSO":
            num = 1
        elif values["COMBOBOX"+str(i)] =="FLOCKING":
            num=2

        #li=[values["LAT"+str(i)],values["LON"+str(i)],values["COMBOBOX"+str(i)],values["SPEED"+str(i)],values["ALTITUDE"+str(i)]]
        li = [float(values["LAT" + str(i)]), float(values["LON" + str(i)]), num, int(values["SPEED" + str(i)]),int(values["ALTITUDE"+str(i)])]

        wp_list.append(li)
        parameters["WAYPOINTS"].append(li)
    dump_wp_file = open("wp_list", "wb")
    pickle.dump(wp_list, dump_wp_file)
    dump_wp_file.close()
    print("waypoint saved to waypoint_list",parameters["WAYPOINTS"])




def listen_to_server(my_ip, listener):
    pack_dict={}

    recv_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        my_ip = "0.0.0.0"  # overiding my IP
        recv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_soc.bind((my_ip, 20010))
        print("BINDED To IP", my_ip)
    except Exception as err:
        listener = False
        print(my_ip)
        print("Error in listener: ", err)

    while listener:
        try:

            data, addr = recv_soc.recvfrom(1024)
            data = json.loads(data)  # data is a dictionary with MESSAGE, SYS_ID , PAYLOAD AS KEYS
            """
            dt["MESSAGE"] = message
                    dt["SYS_ID"] = int(sysid)
                    if payload:
                        dt["PAYLOAD"] = payload
                    else:
                        dt["PAYLOAD"] = []
            """

            if data:
                if data["SYS_ID"] not in pack_dict.keys():
                    pack_dict[data["SYS_ID"]]=data
                    print("RECEIVED FROM UAV:-", addr, data)

                elif data['PACKET_NO'] > pack_dict[data["SYS_ID"]]['PACKET_NO'] or data["PACKET_NO"]==0:
                    """
                    if data["PAYLOAD"]=="REQUEST_TIME":
                        send_mode=1 #ROUTING
                        date_time = str(datetime.now())
                        print("GCS_TIME", datetime)
                        date, clock_time = date_time.split(" ")
                        year, month, day = date.split("-")
                        hour, minute, sec_t = clock_time.split(":")
                        seconds = sec_t[0:2]
                        date_string = month + day + hour + minute + year + "." + seconds
                        message = "TIME"
                        sysid = int(data["SYS_ID"])
                        TIME_thread = threading.Thread(target=send_to_uav,args=(message, sysid, send_mode, str(date_string)))
                        TIME_thread.start()
                    """
                    pack_dict[data["SYS_ID"]] = data
                    print("RECEIVED FROM UAV:-", addr, data)

        except Exception as err:
            print("Error",err)


def Start_mission_func():
    os.chdir("/home/aniket/IAF/GUI")
    os.system("python start_mission.py")

Mission_Data_tab_layout = [
    [sg.Text('Enter the Number of UAVs', size=(36, 1), justification='right'), sg.InputText("", key="NUM_OF_UAV")],
    [sg.Text('Enter the UAV_ID that will remain in front', size=(36, 1), justification='right'),
     sg.InputText("", key="FRONT_UAV_ID")],
    [sg.Text('Enter the min distance between UAVs', size=(36, 1), justification='right'),
     sg.InputText("", key="MIN_DIST")],
    [sg.Text('_' * 125, size=(100, 1), justification='center')],
    [sg.InputText("DTU", size=(6,1),key="map_gps"),sg.Button('Enable Ad-hoc Mode', button_color=('white', '#033F63')),
     sg.Button('Disable Ad-hoc Mode', button_color=('white', '#033F63')),
     sg.Button('Show Map', button_color=('white', '#033F63')),
     sg.Button('LAND ALL SSH', button_color=('white', '#EE6C4D')),sg.Button("Update Mission", button_color=('white', '#033F63'))],
    [sg.Button('Plan Mission', button_color=('white', '#033F63')),
     sg.Button('Load Waypoints', button_color=('white', '#033F63')),
     sg.Button('Save Params', button_color=('white', '#033F63')),sg.Button('Read Params', button_color=('white', '#033F63')),
     sg.Button('Plan Formation', button_color=('white', '#033F63')),
     sg.Button('Upload Mission', button_color=('white', '#033F63'))],
    [sg.Text('_' * 125, size=(100, 1), justification='center')],
    [sg.Button('Start Mission', button_color=('white', 'green')),
     sg.Button('ARM ALL', button_color=('white', 'green')),sg.Button('Land All UAVs', button_color=('white', '#EE6C4D')),sg.Button('RTL All UAVs', button_color=('white', '#EE6C4D')),sg.Button('RESET TIME', button_color=('white', 'green'))],
    [sg.Text('UAV_No', size=(10, 1), justification='left'), sg.InputText("", size=(6, 1), key="UAV_NO"),sg.InputCombo(('STABILIZE','POSHOLD',"GUIDED","GUIDED_NOGPS",'LAND', 'RTL',"ALT_HOLD","AUTO"), size=(10, 3),key="FLIGHT_MODE"),sg.Button('MODE', button_color=('white', '#EE6C4D')),
     sg.Button('RTL', button_color=('white', '#EE6C4D')), sg.Button('LAND', button_color=('white', '#EE6C4D')),
     sg.Button('TAKEOFF', button_color=('white', '#EE6C4D')),sg.InputText("2", key="TAKEOFF_VAR",size=(3,1)), sg.Button('ARM', button_color=('white', '#EE6C4D')),
     sg.Button('DISARM', button_color=('white', '#EE6C4D'))],
    [sg.InputText("8", key="SERVONO",size=(5,1)),sg.InputText("1100", key="PWM",size=(9,1)),sg.Button('SET SERVO', button_color=('white', '#033F63')), sg.Button('READ SERVO', button_color=('white', '#033F63')),sg.Button('FEED', button_color=('white', '#033F63')), sg.Button('PAYLOAD', button_color=('white', '#033F63')),
     sg.Button('STATE', button_color=('white', '#033F63')),  sg.Button('ARM AND STABILIZE', button_color=('white', '#EE6C4D'))],
    [sg.Button('ENGINE HIGH', button_color=('white', '#EE6C4D')), sg.Button('ENGINE MID', button_color=('white', '#033F63')),
     sg.Button('ENGINE LOW', button_color=('white', '#033F63')),sg.Button('REBOOT PIXHAWK', button_color=('white', '#033F63')),sg.Button('LAND SSH', button_color=('white', '#EE6C4D')),sg.Button('POINT2POINT', button_color=('white', '#033F63'),key="toggle_button")],
    [sg.Text('_' * 125, size=(100, 1), justification='center')],
    [sg.Text('IP', size=(8, 1), justification='center'),sg.InputText("192.168.@.@",size=(15, 1), key="IP"),sg.Text('PORT', size=(10, 1), justification='center'),sg.InputText("0.0.0.0",size=(10, 1), key="PORT"),sg.Text('RTP_PORT', size=(15, 1), justification='center'),sg.InputText("0.0.0.0",size=(10, 1), key="RTP"),sg.Button('STREAM', button_color=('white', '#033F63')),sg.Button('DESTREAM', button_color=('white', '#033F63'))],

]


geolocation=0.0
total_num_wp=10

Flight_Plan_tab_layout = [ [sg.Text('WAYPOINT NUM' , size=(15, 1), justification='right') ,sg.Text('LATITUDE ', size=(10, 1), justification='right') ,sg.Text('LONGITUDE ', size=(13, 1), justification='right'),sg.Text('WP TYPE', size=(13, 1), justification='right'),sg.Text('SPEED ', size=(15, 1), justification='right') ,sg.Text('ALTITUDE', size=(15, 1), justification='right') ]]
Flight_Plan_tab_layout += [[ sg.Column([[sg.Text('WAYPOINT '+str(i), size=(15, 1), justification='right',key="TEXT"+str(i)),sg.InputText(str(geolocation),size=(10, 1), key="LAT"+str(i)),sg.InputText(str(geolocation),size=(10, 1), key="LON"+str(i)),sg.InputCombo(('WAYPOINT', 'FLOCKING','MOPSO'), size=(20, 3),key="COMBOBOX"+str(i)),sg.InputText("0.0",size=(10, 1), key="SPEED"+str(i)),sg.InputText("0.0",size=(10, 1), key="ALTITUDE"+str(i))]]
,key="COL"+str(i))]for i in range(total_num_wp)]
Flight_Plan_tab_layout+=[[sg.Button('SHOW WAYPOINT', button_color=('white', '#EE6C4D')), sg.Button('HIDE WAYPOINT', button_color=('white', '#033F63')),sg.Button('Read Waypoints', button_color=('white', 'green')),sg.Button('Save Waypoints', button_color=('white', 'green'))]]


Parameters_tab_layout = [
    [sg.Text('Enter Waypoint_Radius', size=(36, 1), justification='right'),
     sg.InputText("", key="WP_RAD")],
    [sg.Text('Enter Takeoff Altitude', size=(36, 1), justification='right'),
     sg.InputText("", key="TAKEOFF_ALTI")],
    [sg.Text('Enter search Altitude', size=(36, 1), justification='right'),
     sg.InputText("", key="SEARCH_ALTI")],
    [sg.Text('Enter Takeoff Speed', size=(36, 1), justification='right'),
     sg.InputText("", key="TRANSITION_SPEED")],
    [sg.Text('Enter search speed', size=(36, 1), justification='right'),
     sg.InputText("", key="SEARCH_SPEED")],
    [sg.Text('Enter Search Area Length', size=(36, 1), justification='right'),
     sg.InputText("", key="SEARCH_AREA_LENGTH")],
    [sg.Text('Enter Search Area Breadth', size=(36, 1), justification='right'),
     sg.InputText("", key="SEARCH_AREA_BREADTH")],
    [sg.Text('Enter Heading of Search Area', size=(36, 1), justification='right'),
     sg.InputText("", key="HEADING")],
    [sg.Text('Enter Vertical FOV of camera', size=(36, 1), justification='right'),
     sg.InputText("", key="CAMERA_VERTICAL_FOV")],
    [sg.Text('Enter Horizontal FOV of camera', size=(36, 1), justification='right'),
     sg.InputText("", key="CAMERA_HORIZONTAL_FOV")],
    [sg.Text('_' * 100, size=(80, 1), justification='center')],
    [sg.Button('Save Swarm Parameters', button_color=('white', 'green'))],
]


Tuning_Center_tab_layout = [
    [sg.Text('P Controller'),sg.Slider(range=(1,100),default_value=1,size=(25,15),orientation='horizontal',font=('Helvetica', 8),key="P")],
    [sg.Text('I Controller '),sg.Slider(range=(1,100),default_value=1,size=(25,15),orientation='horizontal',font=('Helvetica', 8),key="I")],
    [sg.Text('D Controller'),sg.Slider(range=(1,100),default_value=1,size=(25,15),orientation='horizontal',font=('Helvetica', 8),key="D")],
    [sg.Text('Formation Control'),sg.Slider(range=(1,100),default_value=1,size=(25,15),orientation='horizontal',font=('Helvetica', 8),key="Formation_control")],
    [sg.Text('Flocking Control'),sg.Slider(range=(1,100),default_value=1,size=(25,15),orientation='horizontal',font=('Helvetica', 8),key="Flocking_control")],
    [sg.Button('Upload Tuning Parameters', button_color=('white', 'green'))]
]

home_layout = [[sg.Text('Swarm Planner', size=(27, 1), font=("Helvetica", 25), text_color='#033F63', justification='left'),sg.Image("logo_50.png")],
               [sg.Text('=' * 125, size=(10, 1), justification='center')],
               [sg.TabGroup([[sg.Tab('Mission_Data', Mission_Data_tab_layout), sg.Tab('Flight Plan', Flight_Plan_tab_layout), sg.Tab('Parameters', Parameters_tab_layout), sg.Tab('Tuning Center', Tuning_Center_tab_layout)]])],
               [sg.Button('Read')]]
parameters = {"SWARM_PARAMETERS":{},"WAYPOINTS":[],"SWARM_TUNING_PARAMETERS":{},"TUNING_PARAMETERS":{},"COORDINATES":[],"GEOFENCE":[]}
successful_sent = []
unsuccessful_sent = []
stream_list=[]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_ip = ""
uav_dict = {"INTEL":{},"DTC":{},"GCS":[]}
UAV_INFO = {}
packet_num=1



with open("gcs_list.txt", "r+") as file_hd:
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
        except:
            gcs_or_uav = "UAV"
            ip = "0.0.0.0"
            host_name = "uas-dtu"
            password = "Aether"
            baud = 57600
            interface = "INTEL"
        uav_id = int(ip.split(".")[3]) % 100  # self note : weak logic think something else
        if gcs_or_uav.upper() == "GCS":
            uav_dict["GCS"].append((ip,20010))
            #self.gcs_ip = ip
        else:

            if interface.upper() == "DTC":
                uav_dict["DTC"][uav_id] = (ip,20000)
                uav_dict["INTEL"][uav_id] = (ip, 20000)
                UAV_INFO[uav_id] = data
            elif interface.upper() == "INTEL" :
                uav_dict["INTEL"][uav_id] = (ip,20000)
                UAV_INFO[uav_id] = data

if __name__ == "__main__":

    #Set_Ad_hoc_func()
    #Set_Ad_hoc_func()
    print(uav_dict)
    print(UAV_INFO)
    listener = True
    listen_thread = threading.Thread(target=listen_to_server, args=(my_ip, listener))
    listen_thread.start()

    win = sg.Window('UAS-DTU Swarm Planner', home_layout, auto_size_text=True, default_element_size=(60, 1)).Finalize()
    line_num = 0
    packet_num=1
    send_mode=0  # 0=p2p  1=routing 2= broadcast
    for i in range(total_num_wp):
        linevisibility_setting("HIDE", i)
        pass
    win.Refresh()

    while True:
        try:
            event, values = win.Read()

            if values != None:
                print("SOME EVENT HAPPENING ")


            if event == None:
                continue
            """
            if event == "Save Params":
                send_list = [values["NUM_OF_UAV"], values["UAV_ID"], values["MIN_DIST"], values["WAYPOINT_NUM"]]
                print(send_list)
                # params = list(values.values())
                dump_params_file = open("number_of_UAVs", "wb")
                pickle.dump(send_list, dump_params_file)
                dump_params_file.close()
            """
            if event == "Enable Ad-hoc Mode":
                Ad_hoc_thread = threading.Thread(target=Set_Ad_hoc_func)
                Ad_hoc_thread.start()

                if listener != True:
                    print("Started Listening")
                    listener = True
                    listen_thread = threading.Thread(target=listen_to_server, args=(my_ip, listener))
                    listen_thread.start()



            elif event == "Disable Ad-hoc Mode":
                listener = False
                # listen_thread.join()
                Disable_ad_hoc_thread = threading.Thread(target=Disable_Ad_hoc_func)
                Disable_ad_hoc_thread.start()

            elif event == "LISTENER":
                if listener == True:
                    print("Listening")

                else:
                    # listen_thread.join()
                    listener = True
                    print("listener thread started again")
                    listen_thread = threading.Thread(target=listen_to_server, args=(my_ip, listener))
                    listen_thread.start()

            elif event == "Show Map":
                Map_thread = threading.Thread(target=map)
                Map_thread.start()

            elif event == "Land All UAVs":
                message = "LAND"
                sysid = -1
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Land_thread.start()
            elif event == "RTL All UAVs":
                message = "RTL"
                sysid = -1
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Land_thread.start()

            elif event == "ARM":
                message = "ARM"
                sysid = int(values["UAV_NO"])
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Land_thread.start()

            elif event == "ARM ALL":
                message = "STABILIZED_ARM"
                sysid = -1
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Land_thread.start()


            elif event == "ARM AND STABILIZE":
                message = "STABILIZED.ARM"
                sysid = int(values["UAV_NO"])
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Land_thread.start()

            elif event == "DISARM":
                message = "DISARM"

                sysid = int(values["UAV_NO"])
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Land_thread.start()

            elif event == "MODE":
                print("Sending MODE")
                message = "MODE"
                sysid = int(values["UAV_NO"])
                payload=values["FLIGHT_MODE"]
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode,payload))
                L_thread.start()


            elif event == "LAND":
                print("Sending LAND")
                message = "LAND"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                L_thread.start()

            elif event == "LAND SSH":
                successful_sent = []
                unsuccessful_sent = []
                sysid = int(values["UAV_NO"])
                print("LANDING THROUGH SSH", sysid)
                L_thread = threading.Thread(target=target_land_command, args=(sysid,))
                L_thread.start()

            elif event == "LAND ALL SSH":
                successful_sent = []
                unsuccessful_sent = []
                print("LANDING ALL THROUGH SSH")
                L_thread = threading.Thread(target=ssh_land)
                L_thread.start()

            elif event == "RTL":
                print("Sending RTL")
                message = "RTL"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                L_thread.start()

            elif event == "TAKEOFF":
                print("Sending Takeoff")
                message = "TAKEOFF"
                sysid = int(values["UAV_NO"])
                val=int(values["TAKEOFF_VAR"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode,val))
                L_thread.start()

            elif event == "FEED":

                print("Sending FEED")
                message = "FEED"
                sysid = int(values["UAV_NO"])
                print(uav_dict)
                print(uav_dict["INTEL"].keys(),uav_dict["INTEL"])
                if sysid in uav_dict["INTEL"].keys():
                    ip=uav_dict["DTC"][sysid][0]
                    port=7000+sysid
                    rtp_port=25000+sysid
                    win.Element('IP').Update(value=str(ip))
                    win.Element('PORT').Update(value=str(port))
                    win.Element('RTP').Update(value=str(rtp_port))
                    #L_thread = threading.Thread(target=video_start_client, args=(ip, port, rtp_port))
                    #L_thread.start()
                    #L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                    #L_thread.start()
                    win.refresh()
                else:
                    print("SYSID not in uav id ")
            elif event == "STREAM":

                print("STREAM")
                ip =values["IP"]
                port = values["PORT"]
                rtp_port = values["RTP"]
                stream_thread = threading.Thread(target=video_start_client, args=(ip,port,rtp_port))
                stream_thread.start()

            elif event =="DESTREAM":
                try:

                    ip = values["IP"]
                    stream_list.remove(ip)
                    print("stream_list: " ,stream_list)
                except Exception as err:
                    print(err)

            elif event == "PAYLOAD":
                print("Sending PAYLOAD")
                message = "PAYLOAD"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                L_thread.start()

            elif event == "STATE":
                print("Sending STATE")
                message = "STATE"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                L_thread.start()

            elif event == "toggle_button":

                send_mode=(send_mode+1)%3
                win.Element('toggle_button').Update(("POINT2POINT"," ROUTING ",'BROADCAST')[send_mode], button_color=(('white', ('green',"orange","red")[send_mode])))
                win.refresh()

            elif event == "Plan Mission":
                Plan_mission_thread = threading.Thread(target=Plan_mission_func,args=[values["map_gps"]])
                Plan_mission_thread.start()

            elif event == "Save Waypoints":
                Save_wp_thread = threading.Thread(target=Save_wp_func,args=(values,line_num))
                Save_wp_thread.start()

            elif event == "Read Waypoints":
                wp_file = open("wp_list", 'rb')
                waypoint_list = pickle.load(wp_file)
                dt = {}
                dt["WAYPOINTS"] = waypoint_list
                print("WAYPOINT_LIST", dt)

                read_wp_thread = threading.Thread(target=read_wp_func, args=[dt] )
                read_wp_thread.start()
                print("READING_WAYPOINTS")


            elif event == "Kill Map":
                Kill_Map_thread = threading.Thread(
                    target=Kill_map_func)  # Probably wont require any threading to do it.
                Kill_Map_thread.start()

            elif event == "Plan Formation":
                plan_formation_thread = threading.Thread(target=Plan_formation_func)
                plan_formation_thread.start()
                print("DONE")
                # plan_formation_thread.join()

            elif event == "Upload Mission":
                successful_sent = []
                unsuccessful_sent = []
                upload_mission_thread = threading.Thread(target=Upload_mission_func)
                upload_mission_thread.start()

            elif event == "Update Mission":
                successful_sent = []
                unsuccessful_sent = []
                message = "UPDATE"
                sysid = int(values["UAV_NO"])
                payload={}

                parameter_file = open('number_of_UAVs', 'rb')
                param = pickle.load(parameter_file)
                print("Parameters", param)

                c_matrix_file = open('coor_matrix', 'rb')
                coor_matrix = pickle.load(c_matrix_file)
                print("MATRIX", coor_matrix)

                wp_file = open("wp_list", 'rb')
                wp_list = pickle.load(wp_file)
                print("WAYPOINT_LIST", wp_list)

                send_matrix=[]
                for x,y in coor_matrix:
                    send_matrix.append((int(x),int(y)))

                payload["COORDINATES"]=send_matrix

                payload["WAYPOINTS"]=wp_list

                payload["SWARM_PARAMETERS"]=param

                update_mission_thread = threading.Thread(target=send_to_uav,args=(message,sysid,send_mode,payload))
                update_mission_thread.start()

            elif event == "Start Mission":
                message = "TAKEOFF"
                sysid = -1
                val = int(values["TAKEOFF_VAR"])
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode,val))
                Land_thread.start()

            elif event == "ENGINE HIGH":
                message = "ENGINE.HIGH"
                sysid = int(values["UAV_NO"])
                if sysid == -1:
                    print("SENDING_TO_ALL_UAVS")
                EngineHigh_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                EngineHigh_thread.start()

            elif event == "ENGINE MID":
                message = "ENGINE.MID"
                sysid = int(values["UAV_NO"])
                if sysid == -1:
                    print("SENDING_TO_ALL_UAVS")
                Enginemid_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Enginemid_thread.start()

            elif event == "ENGINE LOW":
                message = "ENGINE.LOW"
                sysid = int(values["UAV_NO"])
                if sysid == -1:
                    print("SENDING_TO_ALL_UAVS")
                Enginelow_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Enginelow_thread.start()

            elif event == "REBOOT PIXHAWK":
                message = "REBOOTPIX"
                sysid = int(values["UAV_NO"])
                if sysid == -1:
                    print("SENDING_TO_ALL_UAVS")
                Enginelow_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode))
                Enginelow_thread.start()

            elif event == "SHOW WAYPOINT":
                if line_num<total_num_wp:
                    show_wp_thread = threading.Thread(target=linevisibility_setting, args=("SHOW", line_num,))
                    line_num+=1
                    show_wp_thread.start()
                win.Refresh()

            elif event == "Save Waypoints":

                    save_wp_thread = threading.Thread(target=Save_wp_func, args=(values,line_num))
                    save_wp_thread.start()
                    print("SAVING_WAYPOINTS")

            elif event == "Load Waypoints":

                    load_wp_thread = threading.Thread(target=load_wp_func, args=())
                    load_wp_thread.start()
                    print("LOADING_WAYPOINTS")

            elif event == "HIDE WAYPOINT":
                if line_num>0:
                    line_num-=1
                    hide_wp_thread = threading.Thread(target=linevisibility_setting, args=("HIDE", line_num,))
                    hide_wp_thread.start()
                win.Refresh()

            elif event == 'Upload Tuning Parameters':
                parameters["TUNING_PARAMETERS"]["P"]=values["P"]
                parameters["TUNING_PARAMETERS"]["I"] = values["I"]
                parameters["TUNING_PARAMETERS"]["D"] = values["D"]
                parameters["TUNING_PARAMETERS"]["Formation_control"] = values["Formation_control"]
                parameters["TUNING_PARAMETERS"]["Flocking_control"] = values["Flocking_control"]
                print(parameters["TUNING_PARAMETERS"])

            elif event == 'Save Swarm Parameters':


                parameters["SWARM_TUNING_PARAMETERS"]["WP_RAD"]=values["WP_RAD"]
                parameters["SWARM_TUNING_PARAMETERS"]["TAKEOFF_ALTI"] = values["TAKEOFF_ALTI"]
                parameters["SWARM_TUNING_PARAMETERS"]["SEARCH_ALTI"] = values["SEARCH_ALTI"]
                parameters["SWARM_TUNING_PARAMETERS"]["TRANSITION_SPEED"] = values["TRANSITION_SPEED"]
                parameters["SWARM_TUNING_PARAMETERS"]["SEARCH_SPEED"] = values["SEARCH_SPEED"]
                parameters["SWARM_TUNING_PARAMETERS"]["SEARCH_AREA_LENGTH"] = values["SEARCH_AREA_LENGTH"]
                parameters["SWARM_TUNING_PARAMETERS"]["SEARCH_AREA_BREADTH"] = values["SEARCH_AREA_BREADTH"]
                parameters["SWARM_TUNING_PARAMETERS"]["HEADING"] = values["HEADING"]
                parameters["SWARM_TUNING_PARAMETERS"]["CAMERA_VERTICAL_FOV"] = values["CAMERA_VERTICAL_FOV"]
                parameters["SWARM_TUNING_PARAMETERS"]["CAMERA_HORIZONTAL_FOV"] = values["CAMERA_HORIZONTAL_FOV"]
                print("SAVING SWARM PARAMETERS",parameters["SWARM_TUNING_PARAMETERS"])


            elif event == 'Save Params':
                #send_list = [values["NUM_OF_UAV"], values["FRONT_UAV_ID"], values["MIN_DIST"]]
                send_list=[int(values["NUM_OF_UAV"]), int(values["FRONT_UAV_ID"]), int(values["MIN_DIST"]),float(values["WP_RAD"]), int(values["TAKEOFF_ALTI"]),int(values["SEARCH_ALTI"]),int(values["TRANSITION_SPEED"]),int(values["SEARCH_SPEED"]),int(values["SEARCH_AREA_LENGTH"]),int(values["SEARCH_AREA_BREADTH"]),int(values["HEADING"]),float(values["CAMERA_VERTICAL_FOV"]),float( values["CAMERA_HORIZONTAL_FOV"])]
                print(send_list)
                dump_params_file = open("number_of_UAVs", "wb")
                pickle.dump(send_list, dump_params_file)
                dump_params_file.close()

                parameters["SWARM_PARAMETERS"]["NUM_OF_UAV"]=values["NUM_OF_UAV"]
                parameters["SWARM_PARAMETERS"]["FRONT_UAV_ID"] = values["FRONT_UAV_ID"]
                parameters["SWARM_PARAMETERS"]["MIN_DIST"] = values["MIN_DIST"]


                print(parameters["SWARM_PARAMETERS"])

            elif event == 'Read Params':
                parameter_file = open('number_of_UAVs', 'rb')
                param = pickle.load(parameter_file)
                print("Parameters", parameters)
                win.Element("NUM_OF_UAV").Update(param[0])
                win.Element("FRONT_UAV_ID").Update(param[1])
                win.Element("MIN_DIST").Update(param[2])
                win.Element("WP_RAD").Update(param[3])
                win.Element("TAKEOFF_ALTI").Update(param[4])
                win.Element("SEARCH_ALTI").Update(param[5])
                win.Element("TRANSITION_SPEED").Update(param[6])
                win.Element("SEARCH_SPEED").Update(param[7])
                win.Element("SEARCH_AREA_LENGTH").Update(param[8])
                win.Element("SEARCH_AREA_BREADTH").Update(param[9])
                win.Element("HEADING").Update(param[10])
                win.Element("CAMERA_VERTICAL_FOV").Update(param[11])
                win.Element("CAMERA_HORIZONTAL_FOV").Update(param[12])


            elif event =='Read':
                print(values)
                print(parameters,len(str(parameters)))

            elif event == "RESET TIME":
                time1=time.time()
                date_time = str(datetime.now())
                print("GCS_TIME",datetime)
                date, clock_time = date_time.split(" ")
                year, month, day = date.split("-")
                hour, minute, sec_t = clock_time.split(":")
                seconds = sec_t[0:2]
                date_string = month + day + hour + minute + year + "." + seconds
                message = "TIME"
                sysid = int(values["UAV_NO"])
                if sysid == -1:
                    print("SENDING_TO_ALL_UAVS")
                TIME_thread = threading.Thread(target=send_to_uav, args=(message, sysid,send_mode,str(date_string)))
                TIME_thread.start()
            elif event =="READ SERVO":
                message = "READSERVO"
                sysid = int(values["UAV_NO"])
                payload=values["SERVONO"]
                if sysid == -1:
                    print("SENDING_TO_ALL_UAVS")
                readservo_thread = threading.Thread(target=send_to_uav, args=(message, sysid, send_mode,payload))
                readservo_thread.start()


            elif event =="SET SERVO" :
                message = "SETSERVO"
                sysid = int(values["UAV_NO"])
                payload = [values["SERVONO"],values["PWM"]]
                if sysid == -1:
                    print("SENDING_TO_ALL_UAVS")
                readservo_thread = threading.Thread(target=send_to_uav, args=(message, sysid, send_mode,payload))
                readservo_thread.start()




        except Exception as err:
            print("CARSHED:- " + str(err))
            print("CHECK IF UAV No TEXTBOX IS EMPTY")
            event, values = win.Read()