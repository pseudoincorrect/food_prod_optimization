
from ctypes import *                      # to connect to IMPL CCall''s using the DLL's
from time import clock                    # to capture the time in the machine 
from glob import *                       
import os                                 # connect Python wih the system
import sqlite3                            # Relational Database
import itertools as it                    # combinatorial math
import math
import time
import re

# Set and get the USELOGFILE setting.

setting = c_char_p(("USELOGFILE").encode("utf-8")) 
IMPLuselogfile = server.IMPLretrieveSETTING(setting)
print("USELOGFILE = ",IMPLuselogfile)

# Initialize the environment (IMPL.set) and allocate the IMPL resource-entities (IMPL.mem) i.e., sets, lists,
# catalogs, parameters, variables, constraints, derivatives, expressions and formulas.

######################
# SDK Initialization # 
######################

flag = c_int(0)
rtnstat = server.IMPLroot(fact,flag)
print("Root Return Status = "+str(rtnstat))
rtnstat = server.IMPLreserve(fact,IMPLall,flag)
print("Reserve Return Status = "+str(rtnstat))

# Get the RNNON setting.

setting = c_char_p(("RNNON").encode("utf-8"))
RNNON = -99999
IMPLrnnon = RNNON #server.IMPLretrieveSETTING(setting)
print("RNNON = ",IMPLrnnon)

# "Interface" to the base model-data using the IML file specified ("fact").

######################
## Run Configuration #
###################### 
form = IMPLsparsic
fit = IMPLdiscrete
filter = IMPLlogistics
focus = IMPLoptimization
face = IMPLimport
factor = IMPLfactor
fob = IMPLfob
frames = IMPLframes
furcate = IMPLfurcate

rtnstat = interfaceri.IMPLinterfaceri(fact,form,fit,filter,focus,face,factor,fob,frames,byref(furcate))
														  
# Set the durations of past/present and future time-horizons and the time-period (discrete-time).
#
# * Note that the duration of the future time-horizon (dthf) is identical to the "prediction-horizon"
#   and "control-horizon" found in model predictive control (MPC) theory.

### Add the chronological data.
dthp = -1.0 #time horizon in the past
dthf = 30  #time horizon in the future
dtp  = 1.0    #time step
rtnstat = interacter.IMPLreceiveT(c_double(dthp),c_double(dthf),c_double(dtp))
														  
# "Serialize" the base or static model-data and cycle-data to a binary (unformatted) file which is faster to 
# re-read than the IML(ASCII) flat-file.
#
# * Note that at this point we are establishing a base / static model-data which is over-loaded or incrementally
#   modified during the closed-loop simulation by adding what IMPL calls "openings" and "orders" for the
#   variable- and parameter-feedback.

rtnstat = server.IMPLrender(fact,IMPLall)

# Compute the number of discretized time-periods in the past/present and future time-horizons.

NTP = int(abs(dthp) / dtp)
NTF = int(dthf / dtp)

# Set the names of the unit-operations-port-state structures.

# Stockpiles.
SNAME = [0]*NS
SNAME[0] = "ST1"
SNAME[1] = "ST2"
SNAME[2] = "ST3"

# Shuttle-conveyors (tripper cars).
NSC = 1
SCNAME = [0]*NSC
SCNAME[0] = "SC"

# Tunnels / zones.
NZ = 3
TNAME = [0]*NZ
TNAME[0] = "A"
TNAME[1] = "B"
TNAME[2] = "C"

TNAME_LOWER = [0]*NZ
TNAME_LOWER[0] = 2.0
TNAME_LOWER[1] = 2.0
TNAME_LOWER[2] = 2.0

TNAME_UPPER = [0]*NZ
TNAME_UPPER[0] = 5.0
TNAME_UPPER[1] = 5.0
TNAME_UPPER[2] = 5.0

NF = 3
FNAME = [0]*NF
FNAME[0] = "F1"
FNAME[1] = "F2"
FNAME[2] = "F3"

FFLOW = [0]*NF
FFLOW[0] = 0.5
FFLOW[1] = 0.3
FFLOW[2] = 0.2

# Initialize the real-time data vectors.

# Expected PODS flowrate from the Mine.

PODSFLOW = [0]*1
PODSFLOW[0]  = 1 # 500.0/60.0 * dtp   ###  total amount / total time 

# Lower, upper, and target bounds for stockpiles.
SLOWER = [0]*NS
SLOWER[0] = 0.0 
SLOWER[1] = 0.0
SLOWER[2] = 0.0

SUPPER = [0]*NS
SUPPER[0] = 1000.0
SUPPER[1] = 1000.0
SUPPER[2] = 1000.0

STARGET = [0]*NS
STARGET[0] = 15.0 + 2*NSIM
STARGET[1] = 10.0 + 2*NSIM
STARGET[2] =  8.0 + 2*NSIM
 
# Estimated opening stockpile holdup.
 
### Input from sensing ###

SHOLDUP = [0]*NS
SHOLDUP[0] = SENSING_SIM[NSIM][0] 
SHOLDUP[1] = SENSING_SIM[NSIM][1] 
SHOLDUP[2] = SENSING_SIM[NSIM][2]

# Shuttle-conveyor x tunnel opening setups and when they started in the past/present.

SCTSETUP = [ [ 0 for i in range(NZ) ] for j in range(NSC) ] 
SCTSETUP[0][0] = 1
SCTSETUP[0][1] = 0
SCTSETUP[0][2] = 0

SCTSTART = [ [ 0 for i in range(NZ) ] for j in range(NSC) ] 
SCTSTART[0][0] = -2.0
SCTSTART[0][1] = -1.0
SCTSTART[0][2] = -1.0

# Compute the "time-to-empty" for each stockpile which is simply the opening holdup divided 
# by the estimated feeder flowrate i.e., T2E = HOLDUP / FLOW.

#STIME2EMPTY = [0]*NS
#for i in range (0,NS):
#  STIME2EMPTY[i] = SHOLDUP[i] / FFLOW[i]

# Compute the 1-norm stockpile holdup weights based on opening / current holdup and feeder flowrate 
# to put more priority or weight to holdups that are closer to drawing empty.
# 
# * Note that we use the inverse and square weight to put more emphasis on the smallest times-to-empty.
#   That is, a small time-to-empty has more weight in the objective function.  The square is also to help
#   compensate for the fact that we are solving using an MILP instead of a MIQP which are more expensive 
#   and usually less reliable.
 
## check to delete
SWEIGHT = [0]*NS
for i in range (0,NS):
#  SWEIGHT[i] = -1.0 / (STIME2EMPTY[i])^2.0
  SWEIGHT[i] = -1.0 / 1.0

  # Penalty weight for excursions on lower and upper stockpile holdups.
#
# * Note that the objective function penalty term should always be significantly greater than the 
#   performance 1-norm term if infeasibilities are present.

PENALTYWEIGHT = 1000.0

# Initialize the IMPL objective function terms which must be set as 1D arrays or vectors in
# order to return or retrieve values by-reference.  The other way is to use unsafe_load().

profit = c_double()
performance1 = c_double()
performance2 = c_double()
penalty = c_double()
total = c_double() 

# Initialize the solution variable result vectors.

#values = [0]*(NTP+NTF)

# Objective function values.

#OBJ =  [0]*(NSIM)

# Stockpile holdup values.

#SHU = [ [ 0 for i in range(NS) ] for j in range(NTP+NSIM) ] 

# Shuttle-converyor x tunnel setup values.

#SCTSU = [ [ [ 0 for i in range(NSC) ] for j in range(NZ) ] for  k in range(NTP+NSIM) ]

starttime = time.process_time()

# Refresh the IMPL resource-entities and restore the base / static model-data and cycle-data from the previously 
# rendered or serialized binary file.

rtnstat = server.IMPLrefresh(IMPLall)
rtnstat = server.IMPLrestore(fact,IMPLall)
status = IMPLkeep

# Set the static model-data.

# Shuttle-conveyor x tunnel unit-operation flowrates.
for j in range (0,NSC): # number of conveyors 
    for k in range (0,NZ):  #number of zones or positions 
        uname = c_char_p(str(SCNAME[j]).encode("utf-8"))  
        oname = c_char_p(str(TNAME[k]).encode("utf-8"))  
        lower = c_double(0.0)
        upper = c_double(1000.0)
        rtnstat = interacter.IMPLreceiveUOrate(uname,oname,lower,upper,status)

# UOPS total and tee rate 
lower = c_double(0.0)
upper = c_double(1000.0)
pname = c_char_p(b"i") 
pname2 = c_char_p(b"o") 
sname = c_char_p(b" ")
uname = c_char_p(b"MINE")
oname = c_char_p(b"S")
rtnstat = interacter.IMPLreceiveUOPStotalrate(uname,oname,pname2,sname,lower,upper,status)
rtnstat = interacter.IMPLreceiveUOPSteerate(uname,oname,pname2,sname,lower,upper,status)

for j in range (0,NSC): # number of conveyors 
    for k in range (0,NZ):  #number of zones or positions 
        uname = c_char_p(str(SCNAME[j]).encode("utf-8"))  
        oname = c_char_p(str(TNAME[k]).encode("utf-8"))  
        rtnstat = interacter.IMPLreceiveUOPStotalrate(uname,oname,pname,sname,lower,upper,status)
        rtnstat = interacter.IMPLreceiveUOPStotalrate(uname,oname,pname2,sname,lower,upper,status)
        rtnstat = interacter.IMPLreceiveUOPSteerate(uname,oname,pname,sname,lower,upper,status)
        rtnstat = interacter.IMPLreceiveUOPSteerate(uname,oname,pname2,sname,lower,upper,status)
                            
for j in range (0,NS):
    uname = c_char_p((str(SNAME[j])).encode("utf-8"))
    oname = c_char_p(b" ")
    rtnstat = interacter.IMPLreceiveUOPStotalrate(uname,oname,pname,sname,lower,upper,status)
    rtnstat = interacter.IMPLreceiveUOPStotalrate(uname,oname,pname2,sname,lower,upper,status)
    rtnstat = interacter.IMPLreceiveUOPSteerate(uname,oname,pname,sname,lower,upper,status)
    rtnstat = interacter.IMPLreceiveUOPSteerate(uname,oname,pname2,sname,lower,upper,status)
                        
for j in range (0,NF):
    uname = c_char_p((FNAME[j]).encode("utf-8"))
    oname = c_char_p(b" ")
    rtnstat = interacter.IMPLreceiveUOPStotalrate(uname,oname,pname,sname,lower,upper,status)
    rtnstat = interacter.IMPLreceiveUOPSteerate(uname,oname,pname,sname,lower,upper,status)


# Splitter or spreader unit-operation flowrates.
# 
#uname = c_char_p(b"SC") 
#oname = c_char_p(b"A")
#lower = c_double(0.0)
#upper = c_double(1000.0)
#rtnstat = interacter.IMPLreceiveUOrate(uname,oname,lower,upper,status)
#
#uname = c_char_p(b"SC") 
#oname = c_char_p(b"B")
#lower = c_double(0.0)
#upper = c_double(1000.0)
#rtnstat = interacter.IMPLreceiveUOrate(uname,oname,lower,upper,status)
#
#uname = c_char_p(b"SC") 
#oname = c_char_p(b"C")
#lower = c_double(0.0)
#upper = c_double(1000.0)
#rtnstat = interacter.IMPLreceiveUOrate(uname,oname,lower,upper,status)

# Splitter or spreader unit-operation-port-state yields for out-port-states only.
uname = c_char_p(b"SC") 
oname = c_char_p(b"A")
pname = c_char_p(b"o") 
pname2 = c_char_p(b"i") 
sname = c_char_p(b" ")
lower = c_double(1)
upper = c_double(1)
rtnstat = interacter.IMPLreceiveUOPSyield(uname,oname,pname,sname,lower,upper,status)
rtnstat = interacter.IMPLreceiveUOPSyield(uname,oname,pname2,sname,lower,upper,status)

uname = c_char_p(b"SC") 
oname = c_char_p(b"B")
pname = c_char_p(b"o") 
sname = c_char_p(b" ")
lower = c_double(1)
upper = c_double(1)
rtnstat = interacter.IMPLreceiveUOPSyield(uname,oname,pname,sname,lower,upper,status)
rtnstat = interacter.IMPLreceiveUOPSyield(uname,oname,pname2,sname,lower,upper,status)

uname = c_char_p(b"SC") 
oname = c_char_p(b"C")
pname = c_char_p(b"o") 
sname = c_char_p(b" ")
lower = c_double(1)
upper = c_double(1)
rtnstat = interacter.IMPLreceiveUOPSyield(uname,oname,pname,sname,lower,upper,status)
rtnstat = interacter.IMPLreceiveUOPSyield(uname,oname,pname2,sname,lower,upper,status)

# Stockpile holdups.
for j in range (0,NS):
    uname = c_char_p((str(SNAME[j])).encode("utf-8"))
    oname = c_char_p(b" ")
    lower = c_double(0.0)
    upper = c_double(1000.0)
    rtnstat = interacter.IMPLreceiveUOholdup(uname,oname,lower,upper,status)

# Shuttle-conveyor zero downtime.
uname = c_char_p(b"SC")
onoff = c_char_p(b"on")
rtnstat = interacter.IMPLreceiveUzerodowntime(uname,onoff,status)  

# Shuttle-conveyor x tunnel unit-operation groups to be used with the sequence-dependent "phasing" or "prohibiting".
uname  = c_char_p(b"SC")
oname  = c_char_p(b"A")
ogname = c_char_p(b"AGroup")
rtnstat = interacter.IMPLreceiveUOOG(uname,oname,ogname,status)

oname  = c_char_p(b"B")
ogname = c_char_p(b"BGroup")
rtnstat = interacter.IMPLreceiveUOOG(uname,oname,ogname,status)

oname  = c_char_p(b"C")
ogname = c_char_p(b"CGroup")
rtnstat = interacter.IMPLreceiveUOOG(uname,oname,ogname,status)

oname  = c_char_p(b"A")
ogname = c_char_p(b"AGroup")
oname2  = c_char_p(b"C")
ogname2 = c_char_p(b"CGroup")
operation = c_char_p(b"prohibited") 
rtnstat = interacter.IMPLreceiveUOGOGO(uname,ogname,ogname2,operation,status)
rtnstat = interacter.IMPLreceiveUOGOGO(uname,ogname2,ogname,operation,status)

# Stockpile holdups in the present (openings).
for j in range (0,NS):
    uname = c_char_p((SNAME[j]).encode("utf-8"))
    oname = c_char_p(b" ")
    value = c_double(SHOLDUP[j])
    starttime = c_double(-dtp)
    rtnstat = interacter.IMPLreceiveUOholdupopen(uname,oname,value,starttime,status)
  
## Shuttle-conveyor x tunnel setups and starts in the past and present time-horizon.
#for j in range (0,NSC):
#    for k in range (0,NZ):
#        uname = c_char_p((SCNAME[j]).encode("utf-8")) 
#        oname = c_char_p((TNAME[k]).encode("utf-8"))
#        value = c_double(SCTSETUP[j][k])
#        starttime = c_double(SCTSTART[j][k])
#        rtnstat = interacter.IMPLreceiveUOsetupopen(uname,oname,value,starttime,status) 

# Set the 1-norm performance weights for the stockpiles.
for j in range (0,NS):
    uname = c_char_p((SNAME[j]).encode("utf-8"))
    oname = c_char_p(b" ")
    prowt = c_double(0.0)
    per2wt = c_double(-SWEIGHT[j])
    per1wt = c_double(0.0)
    penwt = c_double(PENALTYWEIGHT)
    rtnstat = interacter.IMPLreceiveUOholdupweight(uname,oname,prowt,per1wt,per2wt,penwt,status)

# PODS flowrates from the Mine in the future time-horizon.
for t in range (0,NTF):
    uname = c_char_p(b"MINE")
    oname = c_char_p(b"S")
    pname = c_char_p(b"o")
    sname = c_char_p(b" ")
    lower = c_double(PODSFLOW[0])
    upper = c_double(PODSFLOW[0])
    target = c_double(IMPLrnnon)
    begintime = c_double(t * dtp)
    endtime = c_double((t+1) * dtp)
    rtnstat = interacter.IMPLreceiveUOPSrateorder(uname,oname,pname,sname,lower,upper,target,begintime,endtime,status)  

# Feeder flowrates to the Mills in the future time-horizon.
for j in range (0,NF):
    uname = c_char_p((FNAME[j]).encode("utf-8"))
    oname = c_char_p(b" ")
    pname = c_char_p(b"i")
    sname = c_char_p(b" ") 
    lower = c_double(FFLOW[j])
    upper = c_double(FFLOW[j])
    target = c_double(IMPLrnnon)
    begintime = c_double(0.0)
    endtime = c_double(dthf)
    rtnstat = interacter.IMPLreceiveUOPSrateorder(uname,oname,pname,sname,lower,upper,target,begintime,endtime,status)
    
# Stockpile holdup orders with targets.
for j in range (0,NS):
    uname = c_char_p((SNAME[j]).encode("utf-8"))
    oname = c_char_p(b" ")
    lower = c_double(SLOWER[j])
    upper = c_double(SUPPER[j])
    target = c_double(STARGET[j])
    begintime = c_double(0.0)
    endtime = c_double(dthf)
    rtnstat = interacter.IMPLreceiveUOholduporder(uname,oname,lower,upper,target,begintime,endtime,status)
  
# Add some "incremental" or "delta" setup orders to fix known logic/binary variables.
uname = c_char_p(b"MINE")
oname = c_char_p(b"S")
lower = c_double(1.0)
upper = c_double(0.0)
begintime = c_double(0.0)
endtime = c_double(dthf)
rtnstat = interacter.IMPLreceiveUOsetuporder(uname,oname,lower,upper,begintime,endtime,status)
  
for j in range (0,NS):
    uname = c_char_p((str(SNAME[j])).encode("utf-8"))
    oname = c_char_p(b" ")
    lower = c_double(1.0)
    upper = c_double(0.0)
    begintime = c_double(0.0)
    endtime = c_double(dthf)
    rtnstat = interacter.IMPLreceiveUOsetuporder(uname,oname,lower,upper,begintime,endtime,status)
  
for j in range (0,NF):
    uname = c_char_p((str(FNAME[j])).encode("utf-8"))
    oname = c_char_p(b" ")
    lower = c_double(1.0)
    upper = c_double(0.0)
    begintime = c_double(0.0)
    endtime = c_double(dthf)
    rtnstat = interacter.IMPLreceiveUOsetuporder(uname,oname,lower,upper,begintime,endtime,status)

# Replicate routine for all UO setup variables      
lower = c_double(0.0)
upper = c_double(1.0)
begintime = c_double(0.0)
endtime = c_double(dthf)
rtnstat = interacter.IMPLreplicateUOsetuporders(lower,upper,begintime,endtime,status)

# Fix UOPS UOPS setup variables      

### Input from sensing ###

uname = c_char_p(b"MINE")
oname = c_char_p(b"S")
pname = c_char_p(b"o")
sname = c_char_p(b" ")
uname2 = c_char_p(b"SC")
oname2 = c_char_p(b"B")
pname2 = c_char_p(b"i")
sname2 = c_char_p(b" ")
lower = c_double(0)
upper = c_double(-1)
begintime = c_double(0)
endtime = c_double(1)
rtnstat = interacter.IMPLreceiveUOPSUOPSsetuporder(uname,oname,pname,sname,uname2,oname2,pname2,sname2,lower,upper,begintime,endtime,status)  

oname2 = c_char_p(b"C")
rtnstat = interacter.IMPLreceiveUOPSUOPSsetuporder(uname,oname,pname,sname,uname2,oname2,pname2,sname2,lower,upper,begintime,endtime,status)  

# Replicate routine for all UOPS UOPS setup variables      
lower = c_double(0.0)
upper = c_double(1.0)
begintime = c_double(0.0)
endtime = c_double(dthf)
rtnstat = interacter.IMPLreplicateUOPSUOPSsetuporders(lower,upper,begintime,endtime,status)

# Update the shuttle-conveyor "up-times" or run-lengths based on stockpile holdup and feeder statuses.

for j in range (0,NSC):
    for k in range (0,NZ):
        uname = c_char_p((SCNAME[j]).encode("utf-8"))
        oname = c_char_p((TNAME[k]).encode("utf-8"))
        lower = c_double(TNAME_LOWER[k])
        upper = c_double(TNAME_UPPER[k]) 
        rtnstat = interacter.IMPLreceiveUOuptime(uname,oname,lower,upper,status) 

#######################
# Construct the Model #
#######################

filler = IMPLfiller
foreign = IMPLforeign
force = IMPLparameter

rtnstat = modelerv.IMPLmodelerv(fact_results,form,fit,filter,focus,filler,foreign,byref(IMPLparameter))
rtnstat = modelerv.IMPLmodelerv(fact_results,form,fit,filter,focus,filler,foreign,byref(IMPLvariable))
rtnstat = modelerc.IMPLmodelerc(fact_results,form,fit,filter,focus,filler,foreign,byref(IMPLconstraint))

# "Presolve and solve" the problem using MILP.

factorizer = IMPLsemisolverless
fresh = IMPLfirstsession
flashback = IMPLflatfile
feedback = IMPLfeedback

#  fork = IMPLcoinmp
#  fork = IMPLglpk
#  fork = IMPLlpsolve
fork = IMPLcplex
#  fork = IMPLgurobi
#  fork = IMPLoptonomy
#  fork = IMPLxpress

#########
# Solve #
#########
INNON = 1

rtnstat = presolver.IMPLpresolver(fact_results,form,fit,filter,focus,factorizer,fork,fresh,flashback,feedback)

######################
# Infeasibility List #
######################

if rtnstat == INNON:
    print ("impl> %ERROR% - Invalid arguments.")
elif rtnstat > 0: 
    print ("impl> %ERROR% - Invalid input = ") 
    print (rtnstat)
elif rtnstat < 0: 
    print ("impl> %ERROR% - Not all variables/constraints converged - see *.tdt file.")
    CONTOL=c_double(1e-6)
    rtnstat = server.IMPLstatics(fact_results,CONTOL)
    
endtime = time.process_time()
# Get the total objective function value and the equality constraint closure 2-norm as IMPL statistics.

setting = c_char_p(b"OBJVALUE")
objvalue = server.IMPLretrieveSTATISTIC(setting)
print("objvalue = ",objvalue)
#OBJ[sim] = objvalue

# * Note that if the equality and inequality constraint closures are significant (say > 0.000001) then this is not
#   a feasible solution.

setting = c_char_p(b"ECLOSURE2")
eclosure2 = server.IMPLretrieveSTATISTIC(setting)
print("eclosure2 = ",eclosure2)

setting = c_char_p(b"ICLOSURE2")
iclosure2 = server.IMPLretrieveSTATISTIC(setting)
print("iclosure2 = ",iclosure2)

setting = c_char_p(b"STATUS")
solverstatus = server.IMPLretrieveSIGNAL(setting)
#if int(solverstatus) == IMPLoptimal:
#  print("status = SOLVED")
#else:
#  print("status = NOT SOLVED")  


# Get the objective function terms where only the performance1 (1-norm, LP) (and penalties) is non-zero i.e., no profit and
# performance2 terms (2-norm, QP).

#   NLP Retrieves to cherry-pick the yields and factors for the remaining MILP iterations (ite >=2)
ntp = c_int()
ntf = c_int()
interacter.IMPLretrieveT(byref(ntp),byref(ntf))
print('ntp = ', ntp.value)
print('ntf = ', ntf.value)

profit = c_double()
performance1 = c_double()
performance2 = c_double()
penalty = c_double()
total = c_double() 

interacter.IMPLretrieveOBJterms2(byref(profit),byref(performance1),byref(performance2),byref(penalty),byref(total))
print ('Profit_ID = ',profit)
print ('performance1_ID = ',performance1)
print ('performance2_ID = ',performance2)
print ('penalty_ID = ',penalty)
print ('total_ID = ',total)

profit = str(profit)
performance1 = str(performance1)
performance2 = str(performance2)
penalty = str(penalty)
total = str(total)

string1 = profit.split("c_double(")[1].split(")")[0]
string2 = performance1.split("c_double(")[1].split(")")[0]
string3 = performance2.split("c_double(")[1].split(")")[0]
string4 = penalty.split("c_double(")[1].split(")")[0]
string5 = total.split("c_double(")[1].split(")")[0]

profit = float(string1)
performance1 = float(string2)
performance2 = float(string3)
penalty = float(string4)
total = float(string5)
   
# Create array for storing optimal solution from Calculating routine
array = c_double*(max(ntp.value+ntf.value,1)) 
#array = c_double*(5)
#array[0] = 3
#SC_A =  c_double()
SC_A =  array()
SC_B =  array()
SC_C =  array()

# Retrieve solution for the actuating step
#interacter.IMPLretrieveUOflow1(c_char_p(b"SC"),c_char_p(b"A"),c_double(0),c_double(1),SC_A)
interacter.IMPLretrieveUOPSflow2(c_char_p(b"SC"),c_char_p(b"A"),c_char_p(b"i"),c_char_p(b" "),ntp,ntf,SC_A)
interacter.IMPLretrieveUOPSflow2(c_char_p(b"SC"),c_char_p(b"B"),c_char_p(b"i"),c_char_p(b" "),ntp,ntf,SC_B)
interacter.IMPLretrieveUOPSflow2(c_char_p(b"SC"),c_char_p(b"C"),c_char_p(b"i"),c_char_p(b" "),ntp,ntf,SC_C)

for i in range (1,dthf+1):
    SC_A[i] = round(SC_A[i])
    print("SC_A[",i,"] = ", SC_A[i])
print()
for i in range (1,dthf+1):
    SC_B[i] = round(SC_B[i])
    print("SC_B[",i,"] = ", SC_B[i])
print()
for i in range (1,dthf+1):
    SC_C[i] = round(SC_C[i])
    print("SC_C[",i,"] = ", SC_C[i])
print()


# Write a log message to the IMPL log file (*.ldt).
print (' ')
logmessage = c_char_p(("Iteration # "+str(NSIM+1)).encode("utf-8"))
rtnstat = server.IMPLwritelog(logmessage)

endtime = time.process_time()

print(endtime)
#print(OBJ)

# Write the IMPL export (*.exl) and data files (*.dta or *.adt).

face = IMPLexport
rtnstat = interfacere.IMPLinterfacere(fact_results,form,fit,filter,focus,face,factor,fob,IMPLframes,byref(furcate))

# Write the variable results configured in the OML file.

#face = IMPLoutput
#rtnstat = interfacere.IMPLinterfacere(fact_results,form,fit,filter,focus,face,factor,fob,IMPLframes,byref(furcate))

rtnstat = server.IMPLwriteall(fact_results,IMPLseriesset,IMPLconstant,IMPLconstant)  # dtr
rtnstat = server.IMPLwriteall(fact_results,IMPLsimpleset,IMPLconstant,IMPLconstant)  # dts
rtnstat = server.IMPLwriteall(fact_results,IMPLsymbolset,IMPLconstant,IMPLconstant)  # dty
rtnstat = server.IMPLwriteall(fact_results,IMPLcatalog,IMPLconstant,IMPLconstant)    # dtg
rtnstat = server.IMPLwriteall(fact_results,IMPLlist,IMPLconstant,IMPLconstant)       # dtl
rtnstat = server.IMPLwriteall(fact_results,IMPLparameter,IMPLconstant,IMPLconstant)  # dtp
rtnstat = server.IMPLwriteall(fact_results,IMPLvariable,IMPLconstant,IMPLconstant)   # dtv
rtnstat = server.IMPLwriteall(fact_results,IMPLconstraint,IMPLconstant,IMPLconstant) # dtc
rtnstat = server.IMPLwriteall(fact_results,IMPLformula,IMPLconstant,IMPLconstant)	 # dtf

# Write the IMPL model symbology in the *.ndt file.
# Get the pointer or address to the IMPLmodelerc() routine which is required by the IMPLwritesymbology() routine.
ptr_IMPLmodelerc = c_void_p.from_buffer(modelerc.IMPLmodelerc)
rtnstat = server.IMPLwritesymbology(fact_results,byref(ptr_IMPLmodelerc),IMPLconstant)	

# Write the IMPL model symbology in the report *.rdt and summary *.sdt file.
rtnstat = server.IMPLsummary(fact_results)
rtnstat = server.IMPLreport(fact_results)     

# Release (de-allocate) all of the IMPL resource-entity memory.

rtnstat = server.IMPLrelease(IMPLall)

