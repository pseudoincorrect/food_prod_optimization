import argparse
from random import randrange
import time
from cri_dobot.dobotMagician.dll_files import DobotDllType as dType
import sys
from zmq_client import ZmqClient

# Calibration values
Z_UP = 50
Z_DOWN = -7
X_VAL = 275

# The three fixed points on the rail where the Dobot stops
RAIL_POS_HOME = 10
RAIL_POS_A = 460
RAIL_POS_B = RAIL_POS_A + 125
RAIL_POS_C = RAIL_POS_B + 125


CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"
}


def connect_robot(api):
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("Do not forget to enable the rail in DobotStudio (to be fixed)")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    state = dType.ConnectDobot(api, "", 115200)[0]
    if state == dType.DobotConnect.DobotConnect_NoError:
        print("\nConnected to dobot\n")
    else:
        print("Could not connect to robot, exiting program...")
        sys.exit()


def get_mock_position():
    time.sleep(10)
    return randrange(3)


def print_position(api, short=True):
    position = dType.GetPose(api)
    positionRail = dType.GetPoseL(api)[0]
    if short:
        print("Position: ",
              "\nx:", int(position[0]),
              "| y:", int(position[1]),
              "| z:", int(position[2]),
              "| rail:", int(positionRail),
              )
    else:
        print("Position: ",
              "\nx           :", int(position[0]),
              "\ny           :", int(position[1]),
              "\nz           :", int(position[2]),
              "\nrHead       :", int(position[3]),
              "\njoint1Angle :", int(position[4]),
              "\njoint2Angle :", int(position[5]),
              "\njoint3Angle :", int(position[6]),
              "\njoint4Angle :", int(position[7]),
              "\rrail        :", int(positionRail),
              )


def get_rail_pos(position):
    if (position == 0):
        rail_pos = RAIL_POS_A
    elif (position == 1):
        rail_pos = RAIL_POS_B
    elif (position == 2):
        rail_pos = RAIL_POS_C
    return rail_pos


def init_and_start_conveyor_belt(api):
    STEP_PER_CIRCLE = 360.0 / 1.8 * 10.0 * 16.0
    MM_PER_CIRCLE = 3.1415926535898 * 36.0
    vel = float(20) * STEP_PER_CIRCLE / MM_PER_CIRCLE
    # Set conveyor belt velocity
    dType.SetEMotor(api=api, index=0, isEnabled=1, speed=int(vel), isQueued=1)


def init_robot_params(api):
    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)
    # Clean Command Queue
    dType.SetQueuedCmdClear(api)
    dType.GetQueuedCmdCurrentIndex(api)[0]
    # Async Motion Params Setting
    dType.SetHOMEParams(api=api, x=X_VAL, y=0, z=Z_UP, r=0, isQueued=0)
    dType.SetPTPLParams(api=api, velocity=900, acceleration=200, isQueued=1)


def init_robot_params_alt(api):
    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)
    # Clean Command Queue
    dType.SetQueuedCmdClear(api)
    # Async Motion Params Setting
    dType.SetHOMEParams(api=api, x=250, y=0, z=50, r=0, isQueued=1)
    # Set the velocity and acceleration of the joint co-ordinate axis
    dType.SetPTPJointParams(api=api,
                            j1Velocity=100, j1Acceleration=100, j2Velocity=100,
                            j2Acceleration=100, j3Velocity=100, j3Acceleration=100,
                            j4Velocity=100, j4Acceleration=100, isQueued=1)
    # Set the velocity ratio and acceleration ratio in PTP mode
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)


def wait_command_finish(api, last_ind):
    while(last_ind == dType.GetQueuedCmdCurrentIndex(api)):
        time.sleep(2)


def go_safer_position(api):
    positionL = dType.GetPoseL(api)[0]
    lastIndex = dType.SetPTPWithLCmd(
        api=api,
        ptpMode=1,
        x=250, y=0, z=130,
        rHead=0,
        l=positionL + 20,
        isQueued=0)[0]
    wait_command_finish(api, lastIndex)


def robot_homing(api):
    print_position(api)
    dType.SetQueuedCmdStartExec(api)
    # move the robot arm up
    go_safer_position(api)
    # Async Motion Params Setting
    dType.SetHOMECmd(api, temp=0, isQueued=0)[0]
    time.sleep(30)


def robot_go_home(api):
    position = dType.GetPose(api)
    index = dType.SetPTPWithLCmdEx(api=api, ptpMode=1,
                                   x=X_VAL, y=0, z=Z_UP,
                                   rHead=position[3], l=RAIL_POS_HOME, isQueued=1)[0]
    wait_command_finish(api, index)


def robot_go_intermediate_pos(api):
    position = dType.GetPose(api)
    new_rail_pos = get_rail_pos(0)
    # arm up
    dType.SetPTPCmdEx(api=api, ptpMode=2,
                      x=X_VAL - 70, y=0, z=Z_UP + 70,
                      rHead=position[3], isQueued=1)
    position = dType.GetPose(api)
    dType.SetPTPWithLCmdEx(api=api, ptpMode=1,
                           x=position[0], y=position[1], z=position[2],
                           rHead=position[3], l=new_rail_pos, isQueued=1)


def move_to_position(api, new_position):
    position = dType.GetPose(api)
    new_rail_pos = get_rail_pos(new_position)
    # arm up
    dType.SetPTPCmdEx(api=api, ptpMode=2,
                      x=X_VAL, y=0, z=Z_UP,
                      rHead=position[3], isQueued=1)
    position = dType.GetPose(api)
    dType.SetPTPWithLCmdEx(api=api, ptpMode=1,
                           x=position[0], y=position[1], z=position[2],
                           rHead=position[3], l=new_rail_pos, isQueued=1)
    # arm down
    position = dType.GetPose(api)
    dType.SetPTPCmdEx(api=api, ptpMode=2,
                      x=X_VAL, y=0, z=Z_DOWN,
                      rHead=position[3], isQueued=1)


def move_to_position_without_up(api, new_position):
    position = dType.GetPose(api)
    new_rail_pos = get_rail_pos(new_position)
    # arm up
    position = dType.GetPose(api)
    dType.SetPTPWithLCmdEx(api=api, ptpMode=1,
                           x=X_VAL, y=0, z=Z_DOWN,
                           rHead=position[3], l=new_rail_pos, isQueued=1)


def parse_command_line_arguments():
    print("\nRun this script with \"--home or -m\" option to: ",
          " move the robot to home position")
    print("Run this script with \"--simulate or -s\" option to: ",
          "simulate robot positions without ZeroMQ\n")
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--simulate", action="store_true",
                        help="Generate/Send robot commands")
    parser.add_argument("-m", "--home", action="store_true",
                        help="Move the robot to home position")
    return parser.parse_args()


def stop_robot_and_exit(api):
    print("Exiting Dobot Control")
    robot_go_intermediate_pos(api)
    # move_to_position(api, 0)
    robot_go_home(api)
    dType.SetEMotor(api=api, index=0, isEnabled=1, speed=0, isQueued=1)
    dType.SetQueuedCmdForceStopExec(api)
    dType.SetQueuedCmdClear(api)
    dType.DisconnectDobot(api)
    print("Dobot disconnected !")
    sys.exit()


def main():
    args = parse_command_line_arguments()
    api = dType.load()
    connect_robot(api)
    zmq_client = ZmqClient()

    # init_robot_params(api)
    init_robot_params_alt(api)

    # command line argument --home or -m
    if args.home:
        robot_homing(api)

    init_and_start_conveyor_belt(api)

    robot_go_intermediate_pos(api)
    # move_to_position(api, 0)
    time.sleep(5)

    # initialize last_pos variable to hold the latest Rail position
    last_pos = 0

    while True:
        try:
            # command line argument --simulate or -s
            if args.simulate:
                print("Simulating positions")
                new_position = get_mock_position()
            else:
                print("Getting optimization algorithm")
                new_position = zmq_client.get_pos()

            print("moving robot to position", new_position)

            if (new_position != last_pos):
                move_to_position(api, new_position)

            last_pos = new_position

        except KeyboardInterrupt:
            stop_robot_and_exit(api)


if __name__ == "__main__":
    main()
