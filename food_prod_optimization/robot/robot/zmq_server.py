#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
from random import randrange


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8000")

while True:
    #  Wait for next request from client
    message = socket.recv()
    #print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(10)

    newPos = (randrange(3))
    print(newPos)

    as_bytes = bytes([newPos])
    print(as_bytes)

    #  Send reply back to client
    socket.send(as_bytes)