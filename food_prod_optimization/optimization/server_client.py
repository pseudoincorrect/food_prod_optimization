import queue
import threading
import time
import zmq


commands_host = "tcp://*:5556"
inputs_host = "tcp://localhost:5555"


class ZmqServerClient():

    def __init__(self):
        # Commands to the robot
        self._commands_context = zmq.Context()
        self._commands_socket = self._commands_context.socket(zmq.REP)
        self._commands_socket.bind(commands_host)
        self._commands_q = queue.Queue()
        t_commands = threading.Thread(target=self._commands_serve)
        t_commands.daemon = True
        print("Starting ZeroMQ commands server")
        t_commands.start()
        # Input from video processing
        self._inputs_context = zmq.Context()
        self._inputs_q = queue.Queue()
        self._inputs_socket = self._inputs_context.socket(zmq.REQ)
        self._inputs_socket.connect(inputs_host)
        t_inputs = threading.Thread(target=self._inputs_request)
        t_inputs.daemon = True
        print("Starting ZeroMQ inputs client")
        t_inputs.start()

    def _commands_serve(self):
        while True:
            req = self._commands_socket.recv_string()
            # print("Received command request: %s" % req)
            if self._commands_q.empty():
                res ="none"
            else:
                try:
                    res = self._commands_q.get_nowait()
                    # print("Robot command sent: %s" % res)
                except queue.Empty:
                    res ="none"
            self._commands_socket.send_string(str(res))

    def _inputs_request(self):
        while True:
            # print("Sending inputs request")
            self._inputs_socket.send_string("inputs?")
            #  Get the reply.
            message = self._inputs_socket.recv_string()
            if message != "none":
                print("inputs heights received: ", message)
                self._inputs_q.put(message)
            time.sleep(3.0)

    def push_command_msg(self, msg):
        # ensure only the latest value is in the queue
        if not self._commands_q.empty():
            try:
                msg = self._commands_q.get_nowait()
            except queue.Empty:
                pass
        self._commands_q.put(msg)

    def get_input_blocking(self):
        while self._inputs_q.empty():
            time.sleep(1.0)
        try:
            msg = self._inputs_q.get_nowait()
        except queue.Empty:
            return None
        return msg
        