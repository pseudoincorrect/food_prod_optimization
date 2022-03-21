
from cri_dobot.dobotMagician.dll_files import DobotDllType as dType
from zmq_client import get_pos

api = dType.load()

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}


def yes_or_no(question):
    """ Get a y/n answer from the user
    """
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False


# Try and connect to dobot with automatic search, returns enumerate type
state = dType.ConnectDobot(api, "", 115200)[0]
print("Returned value from ConnectDobot command: {}".format(state)) 
print("Connect status meaning:", CON_STR[state])

# If connection is successful
if (state == dType.DobotConnect.DobotConnect_NoError):
    # Check if homing is required
    print("")
    homeRobot = yes_or_no("Do you want to home the robot? ")

    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)  # Stop running commands in command queue

    # Clean Command Queue
    dType.SetQueuedCmdClear(api)  # Clear queue
    currentIndex = dType.GetQueuedCmdCurrentIndex(
        api)[0]  # Get the current command index

    # Async Motion Params Setting
    dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued=1)  # Set home position

    # Set the velocity and acceleration of the joint co-ordinate axis in the format given in DobotDllType.py
    dType.SetPTPJointParams(api, 200, 200, 200, 200,
                            200, 200, 200, 200, isQueued=1)

    # Set the velocity ratio and acceleration ratio in PTP mode
    # (i guess the amount of time it accelerates to define the velocity profile?)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

    # Execute homing function if homing is desired
    if homeRobot:
        # Start homing function
        print("Start homing function immediately (synchronous)")
        # Execute the homing function. Note temp is not used by Dobot. Returned value is the last index ->
        # "queuedCmdIndex: If this command is added to the queue,
        # queuedCmdIndex indicates the index of this command in the queue. Otherwise, it is invalid."
        lastIndex = dType.SetHOMECmd(api, temp=0, isQueued=0)[0]
        print("ReturnHoming: {}".format(lastIndex))

    # Execute commands up to homing function
    dType.SetQueuedCmdStartExec(api)  # Start running commands in command queue

    # Get the current command index
    lastIndex = currentIndex = dType.GetQueuedCmdCurrentIndex(api)[0]

    while True:
        new_pos = get_pos()
        print("Synchronous movement starting")

        current_pose = dType.GetPose(api)
        lastIndex = dType.SetPTPWithLCmd(
            api,
            1,
            current_pose[0],
            current_pose[1],
            current_pose[2],
            current_pose[3],
            new_pos*200,
            isQueued=0)[0]

# Disconnect Dobot
dType.DisconnectDobot(api)  # Disconnect the Dobot
print("Dobot disconnected !")
