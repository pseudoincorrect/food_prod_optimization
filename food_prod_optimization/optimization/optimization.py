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

COMMAND_REFRESH_INTERVAL = 60

def extract_values_from_msg(msg: str):
    input_values = [float(i) for i in msg.split(',')]
    del input_values[0]
    return input_values


def read_for_new_values_from_zmq(ser_cli: client.ZmqServerClient):
    input = ser_cli.get_input_blocking()
    return extract_values_from_msg(input)


class Actuate_Thread(threading.Thread):
    '''
    Class that will send new position to the robot each _timeDelta
    positions can be refreshed/restarted 
    '''
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
        print(f"Redirecting robot to stack number: ", SOLUTIONS[self._cnt])
        msg = SOLUTIONS[self._cnt]
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

###############################################################################
# Start of the main program 

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("-s", "--simulate", action="store_true",
                    help="Generate/Send robot commands")
args = parser.parse_args()

start = True

# Read data / information required for initializing the algorithm
exec(compile(open(data_path, 'rb').read(), data_path, 'exec'))

ser_cli = client.ZmqServerClient()

actuate_Thread = Actuate_Thread(3)
t = threading.Thread(target=actuate_Thread.run)
t.daemon = True
print("Starting sending command to robot")
t.start()

# On the first loop, robot command will be refresh without waiting
intervalStart = 0

while True:
    # Wait for new heights values
    inputs = read_for_new_values_from_zmq(ser_cli)
    
    # if we updated too recently we will not run the rest of the loop,
    # instead, we wait for new heights values
    if (time.time() - intervalStart < COMMAND_REFRESH_INTERVAL):
        continue
        
    intervalStart = time.time()
      
    # Input values sent to the algorithm (global variables)
    SENSING_SIM[0][0] = inputs[0]
    SENSING_SIM[0][1] = inputs[1]
    SENSING_SIM[0][2] = inputs[2]

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

    # Actuate the robot with the newly calculated position
    actuate_Thread.restart()

###############################################################################
