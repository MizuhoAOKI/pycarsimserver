""" carsim_server """

import sys
import time
import zmq
import json
from datetime import timedelta
from pycarsimlib.core import CarsimManager

# constant params
CARSIM_DB_DIR = r"C:\Users\Public\Documents\CarSim2022.1_Data"
VEHICLE_TYPE = "normal_vehicle"
SOCKET_CONFIG = "tcp://*:5555"

def is_json(s: str)->bool:
    """ check if 's' follows json format or not """
    try:
        json.loads(s)
    except ValueError as err_msg:
        print(err_msg)
        return False
    return True

def launch_server()->None:
    """ launch carsim_server and call api to run carsim """

    # make socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(SOCKET_CONFIG)

    # make carsim instance
    cm = CarsimManager(
        carsim_db_dir=CARSIM_DB_DIR,
        vehicle_type=VEHICLE_TYPE,
    )

    # start communication
    try:
        while True:
            #  wait for next request from client
            recv_msg = socket.recv()

            if recv_msg.decode() == "close":
                print("[INFO] Termination flag is True. Close connection.")
                socket.close()
                break

            if is_json(recv_msg):
                json_recv_msg = json.loads(recv_msg)
                print(json.dumps(json_recv_msg,indent=2)) # print json contexts

                # parse msg
                delta_time = float(json_recv_msg["dt"])
                IMP_STEER_SW = float(json_recv_msg["control_input"]["IMP_STEER_SW"])
                IMP_FBK_PDL = float(json_recv_msg["control_input"]["IMP_FBK_PDL"])
                IMP_THROTTLE_ENGINE = float(json_recv_msg["control_input"]["IMP_THROTTLE_ENGINE"])
            else:
                print("[ERROR] Invalid message format.")

            # prepare operational signals
            if delta_time > 0.0:
                control_inputs = {
                    "IMP_STEER_SW": IMP_STEER_SW,
                    "IMP_FBK_PDL": IMP_FBK_PDL,
                    "IMP_THROTTLE_ENGINE": IMP_THROTTLE_ENGINE
                }
            else:
                print("[ERROR] received delta_time is invalid. ")
                socket.send_string("close")
                socket.close()
                break

            # update vehicle states
            if delta_time > 0.0:
                observed, terminated, updated_time_sec = cm.step(action=control_inputs, delta_time=timedelta(seconds=delta_time))
                print(observed)

            # check termination flag
            if terminated:
                print("[INFO] Termination flag is True. End of simulation.")
                socket.send_string("close")
                socket.close()
                break

            #  Send reply back to client
            ## データ成型する
            send_msg = json.dumps(observed, indent=2)
            socket.send(send_msg.encode())

    # error handlings
    except KeyboardInterrupt:
        print("[WARNING] Process interrupted with Ctrl + C. ")
    except Exception as err_msg:
        print("[ERROR]", err_msg)

    # close carsim
    cm.close()

    # return status and result path to app.py => compress and download results dir from webapp

if __name__ == "__main__":
    sys.exit(launch_server())
