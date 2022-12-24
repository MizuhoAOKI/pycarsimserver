""" carsim server for windows """
import streamlit as st
from typing import Any
import sys
import subprocess
from PIL import Image
import psutil

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

def init():
    """ initialization processes """
    print("[INFO] Initializing website")

    # initialize session_states
    if "is_connection_active" not in st.session_state:
        st.session_state.is_connection_active = False

    # initialize carsim_satates
    if "is_carsim_active" not in st.session_state:
        st.session_state.is_carsim_active = False

        # for proc in psutil.process_iter():
        #     _buf = ""
        #     try:
        #         _buf = str(proc.exe())
        #     except psutil.AccessDenied:
        #         _buf = "AccessDenied"

        #     if CARSIM_EXE_FILENAME in _buf:
        #         st.session_state.is_carsim_active = True
        #         break

        search_process(CARSIM_EXE_FILENAME)

    # initialize carsim handler
    if "carsim_handler" not in st.session_state:
        st.session_state.carsim_handler = 0

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
    st.markdown("###### Step 1. launch carsim.")
    if st.button("Launch carsim", disabled=st.session_state.is_carsim_active):
        launch_carsim_software()
        refresh_page()

    # check if carsim software is active
    st.markdown("###### Step 2. Check carsim status is True ")
    st.write(" - Carsim status : ", st.session_state.is_carsim_active)

    # button to start receiving command
    st.markdown("###### Step 3. Connect socket ")
    if st.button("Connect", disabled= (st.session_state.is_connection_active or (not st.session_state.is_carsim_active))):
        st.session_state.is_connection_active = True
        refresh_page()





if __name__ == "__main__":
    main()