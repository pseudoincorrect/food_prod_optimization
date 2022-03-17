from enum import Enum
from operator import indexOf
import threading
import dlls.DobotDllType as dType
import client

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}


class Positions(Enum):
    ONE = 1
    TWO = 2
    
    THREE = 3


class Robot_ctrl():
    def __init__(self, get_commands_blocking):
        self.api = dType.load()
        self.state = dType.ConnectDobot(self.api, "", 115200)[0]
        print("Connect status:", CON_STR[self.state])
        self.get_commands_blocking = get_commands_blocking

    def disconnect(self):
        dType.DisconnectDobot(self.api)

    def process(self):
        if (self.state != dType.DobotConnect.DobotConnect_NoError):
            self.disconnect()
        # Clean Command Queued
        dType.SetQueuedCmdClear(self.api)
        # Async Motion Params Setting
        dType.SetHOMEParams(self.api, 200, 200, 200, 200, isQueued=1)
        dType.SetPTPJointParams(self.api, 200, 200, 200, 200,
                                200, 200, 200, 200, isQueued=1)
        dType.SetPTPCommonParams(self.api, 100, 100, isQueued=1)
        # Async Home
        dType.SetHOMECmd(self.api, temp=0, isQueued=1)
        # Async PTP Motion
        self.got_to_position(Positions.ONE)
        self.got_to_position(Positions.TWO)
        self.got_to_position(Positions.ONE)
        self.got_to_position(Positions.THREE)
        index = self.got_to_position(Positions.TOW)

        self.execute_cmd(index)

    def got_to_position(self, position):
        offset_1 = 50
        offset_2 = 0
        offset_3 = -50
        if position == Positions.ONE:
            index = dType.SetPTPCmd(
                self.api, dType.PTPMode.PTPMOVLXYZMode, 200 + offset_1, offset_1, offset_1, offset_1, isQueued=1)[0]
        elif position == Positions.TWO:
            index = dType.SetPTPCmd(
                self.api, dType.PTPMode.PTPMOVLXYZMode, 200 + offset_2, offset_2, offset_2, offset_2, isQueued=1)[0]
        elif position == Positions.THREE:
            index = dType.SetPTPCmd(
                self.api, dType.PTPMode.PTPMOVLXYZMode, 200 + offset_3, offset_3, offset_3, offset_3, isQueued=1)[0]
        self.execute_cmd(index)

    def execute_cmd(self, queue_index):
        # Start to Execute Command Queue
        dType.SetQueuedCmdStartExec(self.api)
        # Wait for Executing Last Command
        while queue_index > dType.GetQueuedCmdCurrentIndex(self.api)[0]:
            dType.dSleep(100)
        # Stop to Execute Command Queued
        dType.SetQueuedCmdStopExec(self.api)


def robot_control():
    commands_client = client.ZmqClient()
    robot = Robot_ctrl(commands_client.get_commands_blocking)
    robot.process()


if __name__ == "__main__":
    robot_control()
