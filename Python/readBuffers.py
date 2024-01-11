from keithleyDriver import Keithley2600
import numpy as np
import math
import time
import pandas as pd
from datetime import datetime
from os import system, name
import serial
import matplotlib.pyplot as plt
import re
from scipy.signal import find_peaks, savgol_filter, peak_widths
from scipy.signal import argrelmax, welch
import pyvisa
from pathlib import Path
import os

# rm = pyvisa.ResourceManager()
# smu = rm.open_resource('TCPIP0::192.168.4.11::INSTR')

# print(rm.list_opened_resources())
# rm.clear()
# smu.clear()
smu = Keithley2600('TCPIP0::192.168.4.11::inst0::INSTR') 

def voltageSweep():
    vList = "(0, 3, 50)"
    smu._query("voltageSweep()")
    # time.sleep(8)
    # smu._write("vSweep" + vList)
    # smu._query("vSweep(0, 2, 50)")
    smu._write("vSweep(0, 2, 50)")
    time.sleep(8)

def currentSweep():
    iList = "(-1e-8, -1e-4, 30)"
    # smu._query("currentSweep()")
    # time.sleep(8)
    smu._write("cSweep" + iList)

def rtsEval():
    parameters = "(-1e-5, 5, 5e-4, 20)"   # (ibias, test time, delay, range)
    smu._query("rtsEvaluation()")
    time.sleep(4)
    smu._write("rtsEval" + parameters)
    time.sleep(10)

def readBuffer():
    cout = smu.read_buffer(smu.smua.nvbuffer1)
    Iref = smu.read_buffer(smu.smub.nvbuffer2)
    voutbyp = smu.read_buffer(smu.node[2].smua.nvbuffer1)
    ipdV = smu.read_buffer(smu.node[2].smub.nvbuffer1)
    print("cout")
    print(cout)
    print("Iref")
    print(Iref)
    print("ipd Voltage")
    print(ipdV)
    print("voutbyp")
    print(voutbyp)
    return voutbyp, cout, ipdV, vin

def clearBuffer():
    smu.smua.nvbuffer1.clear()
    smu.smub.nvbuffer1.clear()
    smu.smua.nvbuffer1.clearcache()
    smu.smub.nvbuffer1.clearcache()

# clearBuffer()
currentSweep()
# voltageSweep()
# rtsEval()
vout, cout, ipdV, vin = readBuffer()

plt.plot(vin, cout)
plt.show(block=True)
# print(vout)
# readBuffer()

