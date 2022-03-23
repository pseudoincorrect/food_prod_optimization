#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import time
import zmq

commands_host = "tcp://localhost:5556"

class ZmqClient():
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        print("Connecting to", commands_host)
        self.socket.connect(commands_host)

    #  Do 10 requests, waiting each time for a response
    def get_pos(self):
        message = "none"
        while(message == "none"):
            print("Sending request...")
            self.socket.send_string("ping")
            message = self.socket.recv_string()
            print("Received reply %s " % ( message))
            time.sleep(3)
        pos = int(message)
        return pos
