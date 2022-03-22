import random
import time
from ctypes import *                 

val_0 = SENSING_SIM[NSIM][0]
val_1 = SENSING_SIM[NSIM][1]
val_2 = SENSING_SIM[NSIM][2]

# ntp = c_int()
# ntf = c_int()
# array = c_double*(max(ntp.value+ntf.value,1)) 
# SC_A =  array()
# SC_B =  array()
# SC_C =  array()

ROBOT_COMMAND = random.randint(0, 2)

# print("        val_0 = ", val_0)
# print("        val_1 = ", val_1)
# print("        val_2 = ", val_2)
# print("ROBOT_COMMAND = ", ROBOT_COMMAND)

# print("--------------------------------------")

time.sleep(3.0)