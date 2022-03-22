
from random import randrange
import time
from cri_dobot.dobotMagician.dll_files import DobotDllType as dType

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

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

def main():
    api = dType.load()
    
    # Try and connect to dobot with automatic search, returns enumerate type
    state = dType.ConnectDobot(api, "", 115200)[0]
    print("Returned value from ConnectDobot command: {}".format(state))
    print("Connect status meaning:", CON_STR[state])

    # If connection is successful
    if (state == dType.DobotConnect.DobotConnect_NoError):
        # Stop to Execute Command Queued
        dType.SetQueuedCmdStopExec(api)  # Stop running commands in command queue

        # Clean Command Queue
        dType.SetQueuedCmdClear(api)  # Clear queue
        currentIndex = dType.GetQueuedCmdCurrentIndex(
            api)[0]  # Get the current command index

        # Async Motion Params Setting
        dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued=1)  # Set home position

        # Set the velocity and acceleration of the joint co-ordinate axis in the format given in DobotDllType.py
        dType.SetPTPJointParams(api, 100, 100, 100, 100,
                                100, 100, 100, 100, isQueued=1)

        # Set the velocity ratio and acceleration ratio in PTP mode
        dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

        # Execute the homing function. Note temp is not used by Dobot. Returned value is the last index ->
        # "queuedCmdIndex: If this command is added to the queue,
        # queuedCmdIndex indicates the index of this command in the queue. Otherwise, it is invalid."
        if True:
            current_pose = dType.GetPose(api)
            print_position(api)
            dType.SetQueuedCmdStartExec(api)
            extend_arm_from_rest_position(api)
            print()
            lastIndex = dType.SetHOMECmd(api, temp=0, isQueued=0)[0]
            # print("lastIndex", lastIndex)
            dType.SetQueuedCmdStartExec(api)
            wait_command_finish(api, lastIndex)
            time.sleep(30)
        else:
            dType.SetQueuedCmdStartExec(api)


        # Get the current command index
        lastIndex = currentIndex = dType.GetQueuedCmdCurrentIndex(api)[0]

        while True:
            new_pos = get_mock_position()
            print("new_pos =", new_pos, ", moving there...")

            current_pose = dType.GetPose(api)
            print()
            print_position(api)

            lastIndex = dType.SetPTPWithLCmd(
                api,
                1,
                current_pose[0],
                current_pose[1],
                current_pose[2],
                current_pose[3],
                new_pos*200 + 100,
                isQueued=0)[0]

            wait_command_finish(api, lastIndex)


    # Disconnect Dobot
    dType.DisconnectDobot(api)  # Disconnect the Dobot
    print("Dobot disconnected !")



if __name__ == "__main__":
    main()
