from driverTest import Keithley2600
#from keithley2600 import Keithley2600
import numpy as np
import math
import time

smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
# smu.smua.trigger.measure.action = smu.smua.ENABLE
# smu.setA_dMeasIV(smu.smua, smu.smub, 0.0000001, 10, .1, 1)
vlist = range(1,10,1)
smu.ten_Vsweep(smu.smua)
time.sleep(1)
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
# smu.eventlog.clear()