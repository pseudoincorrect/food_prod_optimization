
# Authors: Brenno C. Menezes, Mohammed Yaqot, Ashad Islam, and Robert E. Franzoi Junior
# Date: Aug 30th, 2021
# Language: Python 3.71

# This code runs the entire demo application including Sensing (S), Calculating (C), and Actuating (A)

import os
from ctypes import *
from glob import *
from pathlib import Path
import server_client as client

base_path = Path(__file__).parent
data_path = (base_path / "data.py").resolve()
# scb_ql_path = (base_path / "scb_ql.py").resolve()
scb_ql_path = (base_path / "mock_scb_ql.py").resolve()
heights_path = (base_path / "../vision/heights.txt").resolve()

# Read data / information required for initializing the algorithm
exec(compile(
    open(data_path, 'rb').read(),
    data_path,
    'exec'))

def extract_values_from_msg(msg: str):
    input_values = [float(i) for i in msg.split(',')]
    del input_values[0]
    return input_values


def read_for_new_values_from_zmq(ser_cli: client.ZmqServerClient):
    input = ser_cli.get_input_blocking()
    return extract_values_from_msg(input)


def read_for_new_values_from_file():
    with open(heights_path, "rb") as file:
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            file.seek(0)
        last_line = file.readline().decode()
    return extract_values_from_msg(last_line)


def simulate_new_values():
    if NSIM == 0:
        SENSING_SIM[NSIM][0] = 16.0
        SENSING_SIM[NSIM][1] = 10.0
        SENSING_SIM[NSIM][2] = 7.0
    elif NSIM == 1:
        SENSING_SIM[NSIM][0] = 18.0
        SENSING_SIM[NSIM][1] = 12.0
        SENSING_SIM[NSIM][2] = 10.0
    elif NSIM == 2:
        SENSING_SIM[NSIM][0] = 21.0
        SENSING_SIM[NSIM][1] = 15.0
        SENSING_SIM[NSIM][2] = 12.0

ser_cli = client.ZmqServerClient()
for NSIM in range(0, NSIM_MAX):
    # The sensing routine is continuously triggered. 
    # No inputs are required for the sensing routine.
    inputs = read_for_new_values_from_zmq(ser_cli)
    # inputs = read_for_new_values_from_file()
    # inputs = simulate_new_values()

    SENSING_SIM[NSIM][0] = inputs[0]
    SENSING_SIM[NSIM][1] = inputs[1]
    SENSING_SIM[NSIM][2] = inputs[2]

    print("SENSING_SIM[NSIM][0]", SENSING_SIM[NSIM][0])
    print("SENSING_SIM[NSIM][1]", SENSING_SIM[NSIM][1])
    print("SENSING_SIM[NSIM][2]", SENSING_SIM[NSIM][2])
    

    ### Call Optimizing routine ###
    # Inputs from the Optimizing routine are the outputs from the Sensing routine, 
    # which includes the inventories or amounts of each stockpile.
    exec(compile(
    open(scb_ql_path, 'rb').read(),
    scb_ql_path,
    'exec'))

    print(AM_I_EXPORTED)
    # Outputs from the Calculating routine are the active robot position 
    # at each instant of time : (SC_A, SC_B, SC_C).
    # print("SC_A = ", SC_A)
    # print("SC_B = ", SC_B)
    # print("SC_C = ", SC_C)

    # Send data to the actuator
    ser_cli.push_command_msg(ROBOT_COMMAND)
