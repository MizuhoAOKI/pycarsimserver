""" carsim server for windows """
import streamlit as st
from typing import Any
import os
import glob
import sys
import subprocess
from PIL import Image
import shutil
import psutil
from carsim_server import *

# global parameters
CARSIM_EXE_FILENAME = "CarSim_64.exe"
CARSIM_LAUNCH_SH_PATH = r"C:/Users/mizuho/Desktop/CarSim2022.lnk"

# utilities
def refresh_page():
    """ func to reload page """
    st.experimental_rerun()

def launch_carsim_software():
    """ func to launch carsim software """
    CARSIM_LAUNCH_SH_PATH = r"C:/Users/mizuho/Desktop/CarSim2022.lnk"
    try:
        print("[INFO] Launching carsim... ")
        st.session_state.carsim_handler = subprocess.Popen(["start", CARSIM_LAUNCH_SH_PATH], shell=True)
        st.session_state.is_carsim_active = True
        print("[INFO] is_carsim_active : ", st.session_state.is_carsim_active)
    except Exception as err_msg:
        st.session_state.is_carsim_active = False
        print(err_msg)
        return

def search_process(process_name: str)->Any:
    """ search process """
    for proc in psutil.process_iter():
        _buf = ""
        try:
            _buf = str(proc.exe())
        except psutil.AccessDenied:
            pass

        if process_name in _buf:
            st.session_state.is_carsim_active = True
            return proc

    return False

# # Load csv and visualize svg animation
# def gen_svg_anime():
#     """ visualize results with svg animation """

#     # settings
#     CARSIM_CSV_LOG = os.path.join(".", "Results/vehicle_state_log.csv")
#     OUTPUT_SVG_PATH = os.path.join(".", "svg_animation.svg")

#     print("Loading reference path")
#     ref = CSVHandler(glob.glob(VEHICLE_LOG))
#     ref.read_csv(ignore_row_num=1)

#     # Note that timestamp should start from 0.0
#     print("Loading vehicle state log")
#     log = CSVHandler(VEHICLE_LOG)
#     log.read_csv(ignore_row_num=1)

#     print("Generate svg animation")
#     try:
#         svg_visualizer(
#             timestamp=np.ravel(log.points[:,0]), # set timestamp data
#             car_x_ary=np.ravel(log.points[:,1]), car_y_ary=np.ravel(log.points[:,2]), # set vehicle location in x-y plane
#             ref_x_ary=np.ravel(ref.points[:,0]), ref_y_ary=np.ravel(ref.points[:,1]), # set reference path points
#             outputpath=OUTPUT_SVG_PATH # set output path of svg animation
#         )
#     except:
#         print("Error occured and program interruped.")
#         print(f"Check your csv files at {REFERENCE_PATH} and {VEHICLE_LOG}")
#         return False

#     print(f"Successfully output svg animation at {OUTPUT_SVG_PATH}")
#     return True

def init():
    """ initialization processes """
    print("[INFO] Initializing website")

    # initialize session_states
    if "is_connection_active" not in st.session_state:
        st.session_state.is_connection_active = False

    # initialize is_carsim_active
    if "is_carsim_active" not in st.session_state:
        st.session_state.is_carsim_active = False
        search_process(CARSIM_EXE_FILENAME)

    # initialize carsim handler
    if "carsim_handler" not in st.session_state:
        st.session_state.carsim_handler = 0

    # initialize log
    if "log" not in st.session_state:
        st.session_state.log = ""

    # initialize is_latest_result_saved
    if "is_latest_result_saved" not in st.session_state:
        st.session_state.is_latest_result_saved = False

    # layout settings
    st.set_page_config(page_title="carsim", layout="centered")

def main():
    """ main process """
    # init page
    init()

    # title 
    st.title("Carsim Server")

    # eyecatch
    ## load image
    image = Image.open('./media/car.png')
    st.image(image, width=200, output_format="PNG")

    # button to launch carsim software
    st.markdown("###### Step 1. Launch carsim.")
    if st.button("Launch carsim", disabled=st.session_state.is_carsim_active):
        launch_carsim_software()
        refresh_page()
    # check if carsim software is active
    st.write("carsim status : ", st.session_state.is_carsim_active)

    # button to start receiving command
    st.markdown("###### Step 2. Connect socket ")
    if st.button("Connect", disabled= (st.session_state.is_connection_active or (not st.session_state.is_carsim_active))):
        st.session_state.is_connection_active = True
        st.info("Start sending signals.", icon="ℹ")
        if launch_server():
            st.session_state.log = "Carsim run failed. Try again."
        else:
            st.session_state.log = "Carsim run finished successfully."
        st.session_state.is_connection_active = False
        # write svg animation
        
        refresh_page()

    # echo info
    if st.session_state.log:
        st.info(st.session_state.log, icon="ℹ")

    if st.session_state.log == "Carsim run finished successfully.":
        # button to save results
        st.markdown("###### Step 3. Save latest results")
        # clear archives
        if os.path.exists("./lastrun_result.zip"):
            os.remove("./lastrun_result.zip")
        shutil.make_archive('./lastrun_result', format='zip', root_dir='./Results/')
        st.session_state.is_latest_result_saved = True

        if st.session_state.is_latest_result_saved:
            if os.path.exists('./lastrun_result.zip'):
                st.download_button(
                    label="Download Zip",
                    data=open('./lastrun_result.zip', 'br'),
                    file_name='lastrun_result.zip'
                )

if __name__ == "__main__":
    main()