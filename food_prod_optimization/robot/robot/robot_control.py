import argparse
from random import randrange
import time
from cri_dobot.dobotMagician.dll_files import DobotDllType as dType
import sys
from zmq_client import ZmqClient

# Calibration values
Z_UP = 10
Z_DOWN = -65
R_HEAD_VAL = 300

# The three fixed points on the rail where the Dobot stops
RAIL_POS_A = 200
RAIL_POS_B = 400
RAIL_POS_C = 600


CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"
}


def connect_robot(api):
    state = dType.ConnectDobot(api, "", 115200)[0]
    if state == dType.DobotConnect.DobotConnect_NoError:
        print("\nConnected to dobot\n")
    else:
        print("Could not connect to robot")
        exit()


def get_mock_position():
    time.sleep(15)
    return randrange(3)


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


def get_rail_pos(new_pos):
    if (new_pos == 0):
        rail_pos = RAIL_POS_A
    elif (new_pos == 1):
        rail_pos = RAIL_POS_B
    elif (new_pos == 2):
        rail_pos = RAIL_POS_C
    return rail_pos


def start_conveyor_belt(api):
    STEP_PER_CIRCLE = 360.0 / 1.8 * 10.0 * 16.0
    MM_PER_CIRCLE = 3.1415926535898 * 36.0
    vel = float(20) * STEP_PER_CIRCLE / MM_PER_CIRCLE
    # Set sliding rail velocity
    dType.SetEMotor(api, 0, 1, int(vel), 1)


def init_robot_params(api):
    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)
    # Clean Command Queue
    dType.SetQueuedCmdClear(api)
    dType.GetQueuedCmdCurrentIndex(api)[0]
    # Async Motion Params Setting
    dType.SetHOMEParams(api, R_HEAD_VAL, 0, Z_UP, 0, isQueued=0)
    dType.SetPTPLParams(api, 900, 200, 1)
    


def init_robot_params_alt(api):
    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)
    # Clean Command Queue
    dType.SetQueuedCmdClear(api)
    # Async Motion Params Setting
    dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued=1)
    # Set the velocity and acceleration of the joint co-ordinate axis
    dType.SetPTPJointParams(api, 100, 100, 100, 100,
                            100, 100, 100, 100, isQueued=1)
    # Set the velocity ratio and acceleration ratio in PTP mode
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)


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


def extend_arm_from_rest_position(api):
    position = dType.GetPose(api)
    positionL = dType.GetPoseL(api)[0]
    lastIndex = dType.SetPTPWithLCmd(
        api=api,
        ptpMode=1,
        x=250,
        y=0,
        z=130,
        rHead=0,
        l=positionL,
        isQueued=0)[0]
    wait_command_finish(api, lastIndex)


def robot_go_home(api):
    print_position(api)
    dType.SetQueuedCmdStartExec(api)
    # move the robot arm up
    extend_arm_from_rest_position(api)
    # Async Motion Params Setting
    dType.SetHOMECmd(api, temp=0, isQueued=0)[0]
    time.sleep(30)

def parse_command_line_arguments():
    print("Run this script with \"--home or -m\" option to: ",
          " move the robot to home position")
    print("Run this script with \"--simulate or -s\" option to: ",
          "simulate robot positions without ZeroMQ")
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--simulate", action="store_true",
                        help="Generate/Send robot commands")
    parser.add_argument("-m", "--home", action="store_true",
                        help="Move the robot to home position")
    return parser.parse_args()


def main():
    args = parse_command_line_arguments()
    api = dType.load()
    connect_robot(api)
    zmq_client = ZmqClient()

    init_robot_params(api)
    # init_robot_params_alt(api)
    
    if args.home:
        robot_go_home(api)
        
    # start_conveyor_belt(api)

    # exit()

    # initialize last_pos variable to hold the latest Rail position
    last_pos = 0

    while True:
        try:
            position = dType.GetPose(api)
            
            if args.simulate:
                print("Simulating positions")
                new_pos = get_mock_position()
            else:
                print("Getting optimization algorithm")
                new_pos = zmq_client.get_pos()

            new_rail_pos = get_rail_pos(new_pos)
            if (new_pos != last_pos):
                # arm up
                dType.SetPTPCmdEx(api, 2, R_HEAD_VAL, 0,
                                  Z_UP, position[3], 1)
                position = dType.GetPose(api)
                dType.SetPTPWithLCmdEx(
                    api, 1, position[0], position[1], position[2], position[3], new_rail_pos, 1)
                # arm down
                position = dType.GetPose(api)
                dType.SetPTPCmdEx(api, 2, R_HEAD_VAL, 0,
                                  Z_DOWN, position[3], 1)
            last_pos = new_pos
        except KeyboardInterrupt:
            print("Exiting Dobot Control")
            dType.SetEMotor(api, 0, 1, 0, 1)
            dType.SetQueuedCmdForceStopExec(api)
            lastIndex = dType.SetQueuedCmdClear(api)
            dType.DisconnectDobot(api)
            print("Dobot disconnected !")
            sys.exit()


if __name__ == "__main__":
    main()
