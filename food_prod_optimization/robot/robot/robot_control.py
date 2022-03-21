
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Program Purpose and instructions:
#   (Purpose): Purpose is to check whether the synchronous functionality works. This is checked using keyboard commands
#   (Instructions): Follow the instructions in the terminal
#   (Notes): Please note, this program sources the DLL from the cri_dobot library, but it doesn't use any cri_dobot library functionality

# Author: Ben Money-Coomes

# **Version control**

# v1    Inital commit (Copy of asynchronous code)
# v2    Comments updated
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


# ------------------------------------------#
# Imports                                   #
# ------------------------------------------#

# Import the dobot dll
from cri_dobot.dobotMagician.dll_files import DobotDllType as dType
import time  # For sleeping
import keyboard  # For keyboard input
from zmqClient import get_pos

# Load Dll
api = dType.load()  # Load the dll to allow it to be used

# ------------------------------------------#
# Variables                                 #
# ------------------------------------------#

# Error terms
CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}  # a dictionary of error terms as defined a C++ enum in 'DobotType.h file'


# ------------------------------------------#
# Helper functions                          #
# ------------------------------------------#

def yes_or_no(question):
    """ Get a y/n answer from the user
    """
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False


# ------------------------------------------#
# Start of main program                     #
# ------------------------------------------#

print("")
print("========================")
print("")
print("Hello! This program will:")
print("")
print(" 1. Home the dobot magician robot (if selected)")
print(" 2. Demonstrate if synchronous mode interupts the last command (it doesn't)")
print("")
print(" Let's begin...")
print("")
print("========================")
print("")


# Connect Dobot
# Try and connect to dobot with automatic search, returns enumerate type
state = dType.ConnectDobot(api, "", 115200)[0]
print("Returned value from ConnectDobot command: {}".format(state))  # print result
print("Connect status meaning:", CON_STR[state])

# If connection is successful
if (state == dType.DobotConnect.DobotConnect_NoError):  # If we managed to connect to the dobot

    # Then run this code

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
    # Set the velocity ratio and acceleration ratio in PTP mode (i guess the amount of time it accelerates to define the velocity profile?)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

    # Execute homing function if homing is desired
    if homeRobot:
        # Start homing function
        print("Start homing function immediately (synchronous)")
        # Execute the homing function. Note temp is not used by Dobot. Returned value is the last index -> "queuedCmdIndex: If this command is added to the queue, queuedCmdIndex indicates the index of this command in the queue. Otherwise, it is invalid."
        lastIndex = dType.SetHOMECmd(api, temp=0, isQueued=0)[0]
        print("ReturnHoming: {}".format(lastIndex))

    # Execute commands up to homing function
    dType.SetQueuedCmdStartExec(api)  # Start running commands in command queue

    # --- Start of Loop Synchronous movements

    print("")
    print("========================")
    print("")
    print("Starting synchronous control:")
    print("")
    print(" 1. Press 'a' on the keyboard to move to position A")
    print(" 2. Press 'b' on the keyboard to move to position B")
    print(" 2. Press 'c' on the keyboard to move to position C")
    print(" 3. Press 'e' on the keyboard to stop the command queue and clear it")
    print(" 4. Press 'Esc' on the keyboard to exit and disconnect from the dobot magician")
    print("")
    print(" You can visually see with how the schronous control works with python on the dobot magician.")
    print(" Because if you press 'q' then 'w' immediately after each other, the robot arm responds in kind.")
    print(" It is clear that dobot magician arm doesn't respond immediatly. Instead it executes each move,")
    print(" before beginning the next when communicating using python.")
    print("")
    print("========================")
    print("")

    # Initialise keyboard input for loop
    k = ''
    lastIndex = currentIndex = dType.GetQueuedCmdCurrentIndex(
        api)[0]  # Get the current command index

    # loop until escape character is pressed

    while k!= 'esc':
        new_pos = get_pos() #constantly check for new position
        print("Synchronous movement starting")


        current_pose = dType.GetPose(api)
        lastIndex = dType.SetPTPWithLCmd(api, 1, current_pose[0], current_pose[1], current_pose[2], current_pose[3], new_pos*200,
                             isQueued=0)[0]

    while k != 'esc':
        k = keyboard.read_key()

        if k == 'a':
            print("Synchronous movement A starting")
            lastIndex = dType.SetPTPCmd(
                api, dType.PTPMode.PTPMOVLXYZMode, 200, -120, 50, 30, isQueued=0)[0]
        elif k == 'b':
            print("Synchronous movement B starting")
            lastIndex = dType.SetPTPCmd(
                api, dType.PTPMode.PTPMOVLXYZMode, 150, 120, 50, 0, isQueued=0)[0]

        elif k == 'c':
            print("Synchronous movement C starting")

            current_pose = dType.GetPose(api)
            lastIndex = dType.SetPTPWithLCmd(api, 1, current_pose[0], current_pose[1], current_pose[2], current_pose[3], 200, isQueued=0)[0]

        elif k == 'd':
            print("Synchronous movement C starting")

            current_pose = dType.GetPose(api)
            lastIndex = dType.SetPTPWithLCmd(api, 1, current_pose[0], current_pose[1], current_pose[2], current_pose[3], 500, isQueued=0)[0]

        elif k == 'e':
            print("Command Queue force stop and clear...")
            print("Issuing stop command")
            lastIndex = dType.SetQueuedCmdForceStopExec(api)
            print("lastIndex = ", lastIndex)
            print("")
            print("Issuing clear command")
            lastIndex = dType.SetQueuedCmdClear(api)
            print("lastIndex = ", lastIndex)
            print("")
            print("Starting command queue")
            lastIndex = dType.SetQueuedCmdStartExec(api)
            print("lastIndex = ", lastIndex)

        time.sleep(0.2)
        print("loop continuing")
        print("lastIndex = {}".format(lastIndex))


# Disconnect Dobot
dType.DisconnectDobot(api)  # Disconnect the Dobot
print("Dobot disconnected !")



