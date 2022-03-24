from random import randint
import time
import acquisition
import processing
import server
import cv2
import argparse

# To run this code, open a conda terminal and run:
# $ cd %UserProfile%\Documents\food_prod_optimization\food_prod_optimization\vision && conda activate vision_ai
# $ python vision.py


def print_warning_message():
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("Please connect the camera directly to the computer (without USH Hub)")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")


def vision():
    print_warning_message()

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--simulate", action="store_true",
                        help="Generate/send simulated height values")
    args = parser.parse_args()
    serv = server.ZmqServer()

    if args.simulate:
        simulate(serv.push_msg)

    cap = acquisition.VideoCapture(0)
    if not cap.is_opened():
        print("Could not open video device")
        cap.release()
        return
    else:
        print("Opened video device")
    proc = processing.Processing(cap.read, serv.push_msg)
    while(True):
        ret = proc.process_frame()
        if ret:
            print("stopping the program")
            break

    cap.release()
    cv2.destroyAllWindows()


def simulate(push):
    min_val, max_val = 0, 150
    vals, vals_cnt = [], 3
    for i in range(0, vals_cnt):
        vals.append(randint(0, 150))
    while True:
        timeStamp = str(time.time())
        for i in range(0, vals_cnt):
            vals[i] = vals[i] + randint(-10, 10)
        if vals[i] < min_val:
            vals[i] = min_val
        if vals[i] > max_val:
            vals[i] = max_val
        msg = f'{timeStamp},{vals[0]},{vals[1]},{vals[2]}'
        print("simulated heights:", msg)
        print("stack 1:", vals[0])
        print("stack 2:", vals[1])
        print("stack 2:", vals[2])
        push(msg)
        time.sleep(20.0 + randint(0, 20))


if __name__ == "__main__":
    vision()
