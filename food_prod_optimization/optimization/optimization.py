
# Authors: Brenno C. Menezes, Mohammed Yaqot, Ashad Islam, and Robert E. Franzoi Junior
# Date: Aug 30th, 2021
# Language: Python 3.71

# This code runs the entire demo application including Sensing (S), Calculating (C), and Actuating (A)

# cd $home\Documents\food_prod_optimization\food_prod_optimization\optimization
# python optimization.py

import argparse
import os
from ctypes import *
from glob import *
from pathlib import Path
from random import randint
import threading
import time
import server_client as client

base_path = Path(__file__).parent
data_path = (base_path / "data.py").resolve()
scb_ql_path = (base_path / "scb_ql.py").resolve()
mock_scb_ql_path = (base_path / "mock_scb_ql.py").resolve()
heights_path = (base_path / "../vision/heights.txt").resolve()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("-s", "--simulate", action="store_true",
                    help="Generate/Send robot commands")
args = parser.parse_args()

start = True

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


class Actuate_Thread(threading.Thread):

    def __init__(self, timeDelta):
        self._timeDelta = timeDelta
        self._restart = threading.Event()
        self._cnt = 0

    def run(self):
        while True:
            if self._restart.is_set():
                self._restart.clear()
                self._cnt = 0
            self.actuate()
            time.sleep(self._timeDelta)

    def restart(self):
        self._restart.set()

    def actuate(self):
        if self._cnt >= NSIM_MAX:
            self._cnt = 0
        # print()
        # print("All solutionse are:")
        # for i in range (SC_SIZE):
        #     print(f"SOLUTIONS[{i}] = ", SOLUTIONS[i])
        # print()
        print()
        print(f"SOLUTIONS[{self._cnt}] = ", SOLUTIONS[self._cnt])
        msg = SOLUTIONS[self._cnt]
        print("msg = ", msg)
        ser_cli.push_command_msg(msg)
        self._cnt += 1


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


ser_cli = client.ZmqServerClient()

actuate_Thread = Actuate_Thread(3)
t = threading.Thread(target=actuate_Thread.run)
t.daemon = True
print("Starting sending command to robot")
t.start()

while True:
    for NSIM in range(0, 5):
        # The sensing routine is continuously triggered.
        # No inputs are required for the sensing routine.

        inputs = read_for_new_values_from_zmq(ser_cli)

        # inputs = read_for_new_values_from_file()

        SENSING_SIM[0][0] = inputs[0]
        SENSING_SIM[0][1] = inputs[1]
        SENSING_SIM[0][2] = inputs[2]

        print("SENSING_SIM[0][0]", SENSING_SIM[0][0])
        print("SENSING_SIM[0][1]", SENSING_SIM[0][1])
        print("SENSING_SIM[0][2]", SENSING_SIM[0][2])

        ### Call Optimizing routine ###
        # Inputs from the Optimizing routine are the outputs from the Sensing routine,
        # which includes the inventories or amounts of each stockpile.
        if args.simulate:
            exec(compile(
                open(mock_scb_ql_path, 'rb').read(),
                mock_scb_ql_path,
                'exec'))
        else:
            exec(compile(
                open(scb_ql_path, 'rb').read(),
                scb_ql_path,
                'exec'))

        # Outputs from the Calculating routine are the active robot position
        # at each instant of time : (SC_A, SC_B, SC_C).
        # print("SC_A = ", SC_A)
        # print("SC_B = ", SC_B)
        # print("SC_C = ", SC_C)

        # for the first iteration and quickly send command to the robot
        # without waiting for NSIM_MAX iterations
        if start:
            break

    actuate_Thread.restart()
