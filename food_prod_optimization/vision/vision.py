import time
import acquisition
import processing
import server
import cv2


# To run this code
# $ cd C:\Users\bmenezes\Documents\production_robot_ML\vision_optimization\vision && conda activate vision_ai && python vision.py


def vision():
    cap = acquisition.VideoCapture(0)
    if not cap.is_opened():
        print("Could not open video device")
    else:
        print("Opened video device")

    serv = server.ZmqServer()
    proc = processing.Processing(cap.read, serv.push_msg)

    while(True):
        ret = proc.process_frame()
        if ret:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    vision()
