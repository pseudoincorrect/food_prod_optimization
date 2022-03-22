from random import randrange
import time
from cri_dobot.dobotMagician.dll_files import DobotDllType as dType
import sys

import zmq_client

# Calibration values
z_up = 10
z_down = -65
rHeadVal = 300

# The three fixed points on the rail where the Dobot stops
RAIL_POS_A = 200
RAIL_POS_B = 400
RAIL_POS_C = 600

# Load Dll
api = dType.load()  # Load the dll to allow it to be used

# Error terms
CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"
}  # a dictionary of error terms as defined a C++ enum in 'DobotType.h file'

# ------------------------------------------#
# Helper functions                          #
# ------------------------------------------#

def get_mock_position():
    time.sleep(3)
    return randrange(3)


def wait_command_finish(api, lastCommandIndex):
    print()
    print("Waiting for command to execute")
    while(lastCommandIndex == dType.GetQueuedCmdCurrentIndex(api)):
        print("lastCommandIndex =", lastCommandIndex, ", currentIndex =",
              dType.GetQueuedCmdCurrentIndex(api)[0])
        time.sleep(2)
    print("lastCommandIndex =", lastCommandIndex, ", currentIndex =",
          dType.GetQueuedCmdCurrentIndex(api)[0])
    time.sleep(3)
    print("Command executed")


def print_position(api):
    position = dType.GetPose(api)
    positionL = dType.GetPoseL(api)[0]
    print("Position: ",
          "\nx           :", int(position[0]),
          "\ny           :", int(position[1]),
          "\nz           :", int(position[2]),
          "\nrHead       :", int(position[3]),
          "\njoint1Angle :", int(position[4]),
          "\njoint2Angle :", int(position[5]),
          "\njoint3Angle :", int(position[6]),
          "\njoint4Angle :", int(position[7]),
          "\rrail        :", int(positionL),
          )


def extend_arm_from_rest_position(api):
    position = dType.GetPose(api)
    positionL = dType.GetPoseL(api)[0]
    lastIndex = dType.SetPTPWithLCmd(
        api=api,
        ptpMode=1,
        x=position[0],
        y=position[1],
        z=position[2] + 200,
        rHead=position[3],
        l=positionL,
        isQueued=0)[0]
    wait_command_finish(api, lastIndex)


def yes_or_no(question):
    """ Get a y/n answer from the user
    """
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False


def print_position(api):
    position = dType.GetPose(api)
    positionL = dType.GetPoseL(api)[0]
    print("Position: ",
          "\nx           :", int(position[0]),
          "\ny           :", int(position[1]),
          "\nz           :", int(position[2]),
          "\nrHead       :", int(position[3]),
          "\njoint1Angle :", int(position[4]),
          "\njoint2Angle :", int(position[5]),
          "\njoint3Angle :", int(position[6]),
          "\njoint4Angle :", int(position[7]),
          "\rrail        :", int(positionL),
          )


def getRailPos(new_pos):
    if (new_pos == 0):
        rail_pos = RAIL_POS_A
    elif (new_pos == 1):
        rail_pos = RAIL_POS_B
    elif (new_pos == 2):
        rail_pos = RAIL_POS_C
    return rail_pos


# ------------------------------------------#
# Start of main program                     #
# ------------------------------------------#
# Connect Dobot
# Try and connect to dobot with automatic search, returns enumerate type
state = dType.ConnectDobot(api, "", 115200)[0]
print("Returned value from ConnectDobot command: {}".format(state))
print("Connect status meaning:", CON_STR[state])

zmqClient = zmq_client.ZmqClient()

# If connection is successful
if (state == dType.DobotConnect.DobotConnect_NoError): 
    # Check if homing is required
    print("")
    #homeRobot = yes_or_no("Do you want to home the robot? ")
    homeRobot = True
    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)  

    # Clean Command Queue
    dType.SetQueuedCmdClear(api) 
    currentIndex = dType.GetQueuedCmdCurrentIndex(api)[0]  

    # Async Motion Params Setting
    dType.SetHOMEParams(api, rHeadVal, 0, z_up, 0, isQueued=0)  

    # Execute homing function if homing is desired
    # Start homing function
    extend_arm_from_rest_position(api)
    dType.SetQueuedCmdStartExec(api)
    print("Start homing function immediately (synchronous)")
    lastIndex = dType.SetHOMECmd(api, temp=0, isQueued=0)[0]
    wait_command_finish(api, lastIndex)
    time.sleep(30)
    # Execute commands up to homing function
    # dType.SetQueuedCmdStartExec(api)  # Start running commands in command queue

    # --- Start of Loop Synchronous movements

    # loop until Ctrl+C is pressed

    # Set sliding rail velocity
    STEP_PER_CRICLE = 360.0 / 1.8 * 10.0 * 16.0
    MM_PER_CRICLE = 3.1415926535898 * 36.0
    vel = float(20) * STEP_PER_CRICLE / MM_PER_CRICLE
    dType.SetEMotor(api, 0, 1, int(vel), 1)
    dType.SetPTPLParams(api, 900, 200, 1)

    # initialize last_pos variable to hold the latest Rail position
    last_pos = 0

    while True:
        try:
            print("Getting updated positions from server..")
            current_pose = dType.GetPose(api)
            new_pos = zmqClient.get_pos()
            exit()
            new_rail_pos = getRailPos(new_pos)
            if (new_pos != last_pos):
                # arm up
                dType.SetPTPCmdEx(api, 2, rHeadVal, 0,
                                  z_up, current_pose[3], 1)
                current_pose = dType.GetPose(api)
                dType.SetPTPWithLCmdEx(
                    api, 1, current_pose[0], current_pose[1], current_pose[2], current_pose[3], new_rail_pos, 1)
                # arm down
                current_pose = dType.GetPose(api)
                dType.SetPTPCmdEx(api, 2, rHeadVal, 0,
                                  z_down, current_pose[3], 1)
            last_pos = new_pos
        except KeyboardInterrupt:
            print("Exiting Dobot Control")
            dType.SetEMotor(api, 0, 1, 0, 1)
            dType.SetQueuedCmdForceStopExec(api)
            lastIndex = dType.SetQueuedCmdClear(api)
            dType.DisconnectDobot(api)
            print("Dobot disconnected !")
            sys.exit()
