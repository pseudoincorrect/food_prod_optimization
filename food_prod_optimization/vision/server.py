import queue
import threading
import zmq


host = "tcp://*:5555"


class ZmqServer():

    def __init__(self):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(host)
        self._q = queue.Queue()
        t = threading.Thread(target=self._serve)
        t.daemon = True
        print("Starting ZeroMQ server")
        t.start()

    def _serve(self):
        while True:
            req = self._socket.recv_string()
            # print("Received request: %s" % req)
            if self._q.empty():
                res = "none"
            else:
                try:
                    res = self._q.get_nowait()  
                    print("Sending heights data to Optimization program")
                except queue.Empty:
                    res = "none"
            self._socket.send_string(res)
            
    def push_msg(self, msg):
        # ensure only the latest value is in the queue
        if not self._q.empty:
            try:
                msg = self._q.get_nowait()
            except queue.Empty:
                pass
        self._q.put(msg)
  