""" carsim_client just for test """

import zmq
import sys
import time
import json
import numpy as np

SLEEP_TIME=0.1 #[s]
RECEIVER_TIMEOUT = 3 #[s]

def main() -> None:
    """ send command to carsim server """

    #  Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    socket.RCVTIMEO = RECEIVER_TIMEOUT * 1000 # in milliseconds

    # initialize variables to send
    sim_time = 0.0
    dt = SLEEP_TIME

    try:
        # loop forever
        while True:

            # dummy control inputs
            steer_angle = 20 * np.sin(0.1 * sim_time)
            throttle = 2.5 + 2.5 * np.sin(0.5 * sim_time)
            brake = 0.0

            # prepare json message to send
            json_msg = {"dt": dt,
                            "control_input": {\
                                "IMP_STEER_SW" : steer_angle,\
                                "IMP_FBK_PDL" : brake,\
                                "IMP_THROTTLE_ENGINE" : throttle,\
                            }\
                        }
            send_msg = json.dumps(json_msg, indent=2) # convert python object to string
            # send the binarized string message
            socket.send(send_msg.encode())
            print("\nSent following message :")
            print(send_msg)

            # get the reply
            recv_msg = socket.recv()
            print(f"Received reply [ {recv_msg} ]")
            if recv_msg.decode() == "close":
                print("[INFO] Termination flag is True. Close connection.")
                socket.close()
                sys.exit()

            # sleep for a while
            time.sleep(SLEEP_TIME) # sleep for a while
            sim_time += SLEEP_TIME # increment

    # close socket when the process is interrupted.
    except KeyboardInterrupt:
        socket.send(b"close")
        socket.close()

if __name__ == '__main__':
    main()
