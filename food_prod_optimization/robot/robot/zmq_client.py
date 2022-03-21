#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:8000")

#  Do 10 requests, waiting each time for a response
def get_pos():
    while True:
        print("Sending request  …")
        socket.send(b"ping")

        #  Get the reply.
        message = socket.recv()
        pos = int.from_bytes(message, "big")
        print("Received reply %s " % ( pos))
        return pos
