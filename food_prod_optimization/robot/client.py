import queue
import threading
import time
import zmq


commands_host = "tcp://localhost:5556"


class ZmqClient():

    def __init__(self):
        # Input from video processing
        self._commands_context = zmq.Context()
        self._commands_q = queue.Queue()
        self._commands_socket = self._commands_context.socket(zmq.REQ)
        self._commands_socket.connect(commands_host)
        t_commands = threading.Thread(target=self._commands_request)
        t_commands.daemon = True
        print("Starting ZeroMQ Robot Command client")
        t_commands.start()


    def _commands_request(self):
        while True:
            print("Sending command request")
            self._commands_socket.send_string("command?")
            #  Get the reply.
            message = self._commands_socket.recv_string()
            print("Received command reply", message)
            if message != "none":
                self._commands_q.put(message)
            time.sleep(3.0)


    def get_commands_blocking(self):
        while self._commands_q.empty():
            time.sleep(1.0)
        try:
            msg = self._commands_q.get_nowait()
        except queue.Empty:
            return None
        return msg
        
