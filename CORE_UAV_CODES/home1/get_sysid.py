from pymavlink import mavutil
import time
import sys

# Create the connection
master = mavutil.mavlink_connection('/dev/ttyTHS1', baud=57600)
# Wait a heartbeat before sending commands
master.wait_heartbeat()

# Request all parameters
master.mav.param_request_list_send(
    master.target_system, master.target_component
)
while True:
    time.sleep(0.1)
    try:
        message = master.recv_match(type='PARAM_VALUE', blocking=False).to_dict()
        #print('name: %s\tvalue: %d' % (message['param_id'], message['param_value']))
        if message['param_id'] == "SYSID_THISMAV":
            print('name: ', message['param_id'],' value:' ,message['param_value'])
            master.close()
            sys.exit(100+int(message['param_value']))

    except Exception as e:
        print("error" , e)
        
