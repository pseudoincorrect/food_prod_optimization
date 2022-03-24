
from ctypes import *   
from glob import *     
import os              
from pathlib import Path
import pathlib

# Simulation of NSIM iterations
NSIM_MAX = 10
# Number of Stockpiles
NS = 3
# Command for the robotic arm
ROBOT_COMMAND = None
# Size of the Solution Calculating Routine array
SC_SIZE = 30

NSIM = 1

# Create array to store sensing data of each snapshot
SENSING_SIM = []
for i in range(0,NSIM_MAX):
   tmp = []
   for j in range(0,NS):
       tmp.append(0.0)
   SENSING_SIM.append(tmp[:])
   
# SOLUTIONS
SOLUTIONS = [0 for _ in range(SC_SIZE)]

data_folder_path = pathlib.Path(__file__).parent.absolute()

# Set the path to where the IMPL shared objects (DLL's) are located.
os.chdir(b"C:/IMPL")

# server = windll.LoadLibrary("C:/IMPL/IMPLserver.dll")
exec(open(b"C:/IMPL/IMPLpythoninclude.py").read())

# Explicitly declare IMPL's DLL's required by ctypes for Python 3.8 and later.
# * Note that to add to the path you can perform the following statement:
# os.environ["PATH"] = os.path.dirname(__file__) + ';' + os.environ["PATH"]
# os.add_dll_directory("C:/IMPL/")
# os.add_dll_directory("C:/Program Files (x86)/Common Files/Intel/Shared Libraries/redist/intel64_win/compiler")

server = windll.LoadLibrary("C:/IMPL/IMPLserver.dll")
solvers = windll.LoadLibrary("C:/IMPL/IMPLsolvers.dll")
interacter = windll.LoadLibrary("C:/IMPL/IMPLinteracter.dll")
interfaceri = windll.LoadLibrary("C:/IMPL/IMPLinterfaceri.dll")
interfacere = windll.LoadLibrary("C:/IMPL/IMPLinterfacere.dll")
modelerv = windll.LoadLibrary("C:/IMPL/IMPLmodelerv.dll")
modelerc = windll.LoadLibrary("C:/IMPL/IMPLmodelerc.dll")
presolver = windll.LoadLibrary("C:/IMPL/IMPLpresolver.dll")

# Write the IMPL.hdr header file which contains the selected/necessary information to call IMPL from
# other computer programming languages.
rtnstat = server.IMPLwriteheader()

# Specify directory path
sweeping_path = (data_folder_path / "sweeping").resolve()
sweeping_path = str(sweeping_path)
# IMPL expect backslashes
sweeping_path = sweeping_path.replace(os.sep,"/" )

program = "sweeping"
str_fact                            =    sweeping_path + "/" + program   
str_fact_results                    =    sweeping_path + "/results/" + program
byt_fact                            =    bytes(str_fact, 'utf-8') 	
byt_fact_results                    =    bytes(str_fact_results, 'utf-8')         
fact                                =    c_char_p(byt_fact)  
fact_results                        =    c_char_p(byt_fact_results)     
print("fact = ",                         str_fact) 		
print("fact_results = ",                 str_fact_results)


