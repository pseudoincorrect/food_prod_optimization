#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

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
        print("Sending request...")
        self.socket.send_string("ping")
        message = self.socket.recv_string()
        pos = int(message)
        print("Received reply %s " % ( pos))
        return pos
