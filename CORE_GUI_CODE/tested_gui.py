import os
import subprocess
import socket
import pickle
import paramiko
import threading
import PySimpleGUI as sg
import time
from GUI import graphic
from datetime import datetime
from dronekit import connect

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


def Plan_mission_func():
    # os.chdir("/home/parth/ardupilot/ArduCopter")
    print("gnome-terminal -- sim_vehicle.py -v ArduCopter -L saltlake --map &")
    subprocess.check_call("gnome-terminal -- sim_vehicle.py -v ArduCopter -L saltlake --map &", shell=True)


def Save_wp_func(waypoint_num,trans_speed,search_speed):
    vehicle = connect('127.0.0.1:14550')
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    waypoint_list = list()
    i=1
    for cmd in cmds:
        if int(waypoint_num) ==i:

            waypoint_list.append([cmd.x, cmd.y,1,int(search_speed)])
        else:
            waypoint_list.append([cmd.x, cmd.y, 0, int(trans_speed)])
        i+=1

    dump_wp_file = open("wp_list", "wb")
    pickle.dump(waypoint_list, dump_wp_file)
    dump_wp_file.close()
    print("waypoint saved to waypoint_list")
    print(waypoint_list)


def map():
    global uav_dict
    mid_command = ""

    for key in uav_dict.keys():
        ip = "192.168.4.69"
        port = 5000 + key  # port = 5000 + ip   / port= 5100+sys_id
        mid_command += " --master=" + ip + ":" + str(port)
    command = "mavproxy.py " + mid_command + " --map"
    subprocess.check_call(command, shell=True)


def send_to_uav(message, sysid):
    global uav_dict
    global sock
    print(message, sysid)
    if sysid == -1:
        for key in uav_dict.keys():
            try:
                ip = uav_dict[key][0]
                port = 20000
                sock.sendto(message.encode("utf-8"), (ip, port))
                # data,address=sock.recvfrom(1024)
                # data=data.decode("utf-8")
                # print(data)
            except Exception as err:
                print(err)
    elif sysid in uav_dict.keys():
        try:

            ip = uav_dict[sysid][0]
            port = 20000
            sock.sendto(message.encode("utf-8"), (ip, port))
            print(ip,port)
        # data ,address= sock.recvfrom(1024)
        # data = data.decode("utf-8")
        # print(data)
        except Exception as err:
            print(err)
    print("SENT",uav_dict.keys())


def Plan_formation_func():
    weight_matrix = graphic_object.display()
    print("weight_matrix", weight_matrix)
    dump_weight_matrix_file = open("weight_matrix", "wb")
    pickle.dump(weight_matrix, dump_weight_matrix_file)
    dump_weight_matrix_file.close()


def upload_mission(ip, password, total_name):
    try:

        command = "sshpass -p " + password + " scp " + total_name + " uas-dtu@" + ip + ":/home/uas-dtu/Desktop/new_on_uav/"
        print(command)
        subprocess.check_call(command, shell=True)
        print("datab sent to uav " + ip)
        successful_sent.append(ip)

    except:
        print("data not sent to uav " + ip)
        unsuccessful_sent.append(ip)


def Upload_mission_func():

    
    password = "Aether"
    # os.chdir("/home/parth/Desktop/new_on_uav/GUI/")
    prog_name = ["number_of_UAVs", "weight_matrix", "wp_list", "uav_list.txt"]
    total_name = ""
    parameter_file = open('number_of_UAVs', 'rb')
    parameters = pickle.load(parameter_file)
    print("Parameters", parameters)
    d_matrix_file = open('weight_matrix', 'rb')
    matrix = pickle.load(d_matrix_file)
    print("MATRIX", matrix)
    wp_file = open("wp_list", 'rb')
    waypoint_list = pickle.load(wp_file)
    print("WAYPOINT_LIST", waypoint_list)
    thread_list=[]
    for prog in prog_name:
        total_name += " " + prog

    for ip, port in uav_dict.values():
        thrd=threading.Thread(target=upload_mission,args=[ip,password,total_name])
        thread_list.append(thrd)
        thrd.start()
    for thrd in thread_list:
        thrd.join()

    print("successfully_send to ", successful_sent)
    print("not_successfully_send to ", unsuccessful_sent)


def target_land_command(key):
    global UAV_INFO
    _, ip, host_name, password, baudrate = UAV_INFO[key]
    # host_name, password = self.uav_data[ip]_
    OBC_command = "bash /home/" + host_name + "/ssh_land.sh" + " " + str(baudrate)
    command = "sshpass -p " + password + " ssh" + " -X " + host_name + "@" + ip + " " + OBC_command

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


def listen_to_server(my_ip, listener):
    try:
        my_ip="0.0.0.0" # overiding my IP
        recv_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        recv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_soc.bind((my_ip, 20010))
        print("BINDED To IP", my_ip)
    except Exception as err:
        listener = False
        print(my_ip)
        print("Error in listener: ", err)

    while listener:
        try:

            data, address = recv_soc.recvfrom(512)
            data = data.decode("utf-8")

            if data:
                # self.send_soc.sendto(message.encode("utf-8"),self.gcs_address)
                print("RECEIVED FROM UAV:-", address,data)
        except Exception as err:
            print(err)


def Start_mission_func():
    os.chdir("/home/aniket/IAF/GUI")
    os.system("python start_mission.py")


home_layout = [
    [sg.Text('Swarm Planner', size=(22, 1), font=("Helvetica", 25), text_color='#033F63', justification='left'),
     sg.Image("logo_50.png")],
    [sg.Text('=' * 100, size=(80, 1), justification='center')],
    [sg.Text('Enter the Number of UAVs', size=(36, 1), justification='right'), sg.InputText("", key="NUM_OF_UAV")],
    [sg.Text('Enter the UAV_ID that will remain in front', size=(36, 1), justification='right'),
     sg.InputText("", key="UAV_ID")],
    [sg.Text('Enter the min distance between UAVs', size=(36, 1), justification='right'),sg.InputText("", key="MIN_DIST")],
    [sg.Text('WAYPOINT RADIUS (meters)', size=(36, 1), justification='right'), sg.InputText("", key="WP_RAD")],
    [sg.Text('TAKEOFF ALTI (meters)', size=(36, 1), justification='right'), sg.InputText("", key="TAKEOFF_ALTI")],
    [sg.Text('SEARCH ALTI', size=(36, 1), justification='right'), sg.InputText("", key="SEARCH_ALTI")],
    [sg.Text('TRANSITION SPEED', size=(36, 1), justification='right'), sg.InputText("", key="TRANSITION_SPEED")],
    [sg.Text('SEARCH SPEED', size=(36, 1), justification='right'), sg.InputText("", key="SEARCH_SPEED")],
    [sg.Text('SAL', size=(36, 1), justification='right'), sg.InputText("", key="SAL")],
    [sg.Text('SAB', size=(36, 1), justification='right'), sg.InputText("", key="SAB")],
    [sg.Text('HEADING', size=(36, 1), justification='right'), sg.InputText("", key="HEADING")],
    [sg.Text('FOVX', size=(36, 1), justification='right'), sg.InputText("", key="FOV_X")],
    [sg.Text('FOVY', size=(36, 1), justification='right'), sg.InputText("", key="FOV_Y")],
[sg.Text('SEARCH_WAYPOINT NUMBER', size=(36, 1), justification='right'), sg.InputText("", key="SEARCH_WAYPOINT")],

    [sg.Text('_' * 100, size=(80, 1), justification='center')],
    [sg.Button('Enable Ad-hoc Mode', button_color=('white', '#033F63')),
     sg.Button('Disable Ad-hoc Mode', button_color=('white', '#033F63')),
     sg.Button('Show Map', button_color=('white', '#033F63')),
     sg.Button('LAND ALL SSH', button_color=('white', '#EE6C4D'))],
    [sg.Button('Plan Mission', button_color=('white', '#033F63')),
     sg.Button('Save Waypoints', button_color=('white', '#033F63')),
     sg.Button('Save Params', button_color=('white', '#033F63')),
     sg.Button('Plan Formation', button_color=('white', '#033F63')),
     sg.Button('Upload Mission', button_color=('white', '#033F63'))],
    [sg.Text('_' * 100, size=(80, 1), justification='center')],
    [sg.Button('Start Mission', button_color=('white', 'green')),
     sg.Button('ARM ALL', button_color=('white', 'green')),sg.Button('Land All UAVs', button_color=('white', '#EE6C4D'))],
    [sg.Text('UAV_No', size=(10, 1), justification='left'), sg.InputText("", size=(18, 1), key="UAV_NO"),
     sg.Button('RTL', button_color=('white', '#EE6C4D')), sg.Button('LAND', button_color=('white', '#EE6C4D')),
     sg.Button('TAKEOFF', button_color=('white', '#EE6C4D')), sg.Button('ARM', button_color=('white', '#EE6C4D')),
     sg.Button('DISARM', button_color=('white', '#EE6C4D'))],
    [sg.Button('FEED', button_color=('white', '#033F63')), sg.Button('PAYLOAD', button_color=('white', '#033F63')),
     sg.Button('STATE', button_color=('white', '#033F63')), sg.Button('LISTENER', button_color=('white', '#033F63')),
     sg.Button('ARM AND STABILIZE', button_color=('white', '#EE6C4D')),
     sg.Button('LAND SSH', button_color=('white', '#EE6C4D'))],
    [sg.Button('ENGINE HIGH', button_color=('white', '#EE6C4D')), sg.Button('ENGINE MID', button_color=('white', '#033F63')),
     sg.Button('ENGINE LOW', button_color=('white', '#033F63')),sg.Button('RESET TIME', button_color=('white', '#033F63'))],
]

successful_sent = []
unsuccessful_sent = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_ip = ""
uav_dict = {}
UAV_INFO = {}

with open("gcs_list.txt", "r+") as file_hd:
    lines = file_hd.readlines()
    for line in lines:
        try:

            var = line.strip().split()
            print(var)
            if str(var[0]).upper() == "GCS":
                my_ip = str(var[1])

            if str(var[0]).upper() == "UAV":
                ip = str(var[1])
                port = int(var[1].split(".")[3]) - 100 + 5000  # port = 5000 + ip   / port= 5100+sys_id
                sys_id = int(var[1].split(".")[3]) %100
                print(port)
                address = (ip, port)
                uav_dict[sys_id] = address
                UAV_INFO[sys_id] = var  # UAV ip host_name password baudrate
        except Exception as err:
            pass

if __name__ == "__main__":

    # Set_Ad_hoc_func()
    # Set_Ad_hoc_func()

    listener = True
    listen_thread = threading.Thread(target=listen_to_server, args=(my_ip, listener))
    listen_thread.start()

    win = sg.Window('UAS-DTU Swarm Planner', home_layout, auto_size_text=True, default_element_size=(40, 1))

    while True:
        try:
            event, values = win.Read()

            if values != None:
                print("ONLY PRINTING NOT SAVING ",values)
                """
                #send_list=[values[""],values[""],values[""],values[""]]
                params = list(values.values())
                dump_params_file = open("number_of_UAVs", "wb")
                pickle.dump(params, dump_params_file)
                dump_params_file.close()
                """

            if event == None:
                continue
            if event == "Save Params":
                send_list = [values["NUM_OF_UAV"], values["UAV_ID"], values["MIN_DIST"], values["WP_RAD"],values["TAKEOFF_ALTI"],values["SEARCH_ALTI"],values["TRANSITION_SPEED"],values["SEARCH_SPEED"],values["SAL"],values["SAB"],values["HEADING"],values["FOV_X"],values["FOV_Y"]]
                print(send_list)
                #params = list(values.values())
                dump_params_file = open("number_of_UAVs", "wb")
                pickle.dump(send_list, dump_params_file)
                dump_params_file.close()

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
                    listener = False
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
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Land_thread.start()

            elif event == "ARM":
                message = "ARM"
                sysid = int(values["UAV_NO"])
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Land_thread.start()

            elif event == "ARM ALL":
                message = "STABILIZED_ARM"
                sysid = -1
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Land_thread.start()


            elif event == "ARM AND STABILIZE":
                message = "STABILIZED_ARM"
                sysid = int(values["UAV_NO"])
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Land_thread.start()

            elif event == "DISARM":
                message = "DISARM"

                sysid = int(values["UAV_NO"])
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Land_thread.start()


            elif event == "LAND":
                print("Sending LAND")
                message = "LAND"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
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
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                L_thread.start()

            elif event == "TAKEOFF":
                print("Sending Takeoff")
                message = "TAKEOFF"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                L_thread.start()

            elif event == "FEED":
                print("Sending FEED")
                message = "FEED"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                L_thread.start()

            elif event == "PAYLOAD":
                print("Sending PAYLOAD")
                message = "PAYLOAD"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                L_thread.start()

            elif event == "STATE":
                print("Sending STATE")
                message = "STATE"
                sysid = int(values["UAV_NO"])
                L_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                L_thread.start()

            elif event == "Plan Mission":
                Plan_mission_thread = threading.Thread(target=Plan_mission_func)
                Plan_mission_thread.start()

            elif event == "Save Waypoints":

                Save_wp_thread = threading.Thread(target=Save_wp_func,args=(values["SEARCH_WAYPOINT"],values["TRANSITION_SPEED"],values["SEARCH_SPEED"]))
                Save_wp_thread.start()

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
                successful_sent=[]
                unsuccessful_sent=[]
                upload_mission_thread = threading.Thread(target=Upload_mission_func)
                upload_mission_thread.start()

            elif event == "Start Mission":
                message = "TAKEOFF"
                sysid = -1
                Land_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Land_thread.start()

            elif event =="ENGINE HIGH":
                message = "ENGINE_HIGH"
                sysid = int(values["UAV_NO"])
                if sys_id ==-1:
                    print("SENDING_TO_ALL_UAVS")
                EngineHigh_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                EngineHigh_thread.start()

            elif event == "ENGINE MID":
                message = "ENGINE_MID"
                sysid = int(values["UAV_NO"])
                if sys_id == -1:
                    print("SENDING_TO_ALL_UAVS")
                Enginemid_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Enginemid_thread.start()

            elif event == "ENGINE LOW":
                message = "ENGINE_LOW"
                sysid = int(values["UAV_NO"])
                if sys_id == -1:
                    print("SENDING_TO_ALL_UAVS")
                Enginelow_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Enginelow_thread.start()

            elif event == "RESET TIME":
                time1=time.time()
                date_time = str(datetime.now())
                print("GCS_TIME",datetime)
                date, clock_time = date_time.split(" ")
                year, month, day = date.split("-")
                hour, minute, sec_t = clock_time.split(":")
                seconds = sec_t[0:2]
                date_string = month + day + hour + minute + year + "." + seconds
                message = "TIME_" +str(date_string)
                sysid = int(values["UAV_NO"])
                if sys_id == -1:
                    print("SENDING_TO_ALL_UAVS")
                Enginelow_thread = threading.Thread(target=send_to_uav, args=(message, sysid,))
                Enginelow_thread.start()


        except Exception as err:
            print("CARSHED:- " + str(err))
            print("CHECK IF YOU ENTER TEXT IN TEXTBOX")
            event, values = win.Read()