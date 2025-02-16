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
import pywt
from scipy.signal import find_peaks, find_peaks_cwt, savgol_filter, gaussian, convolve
from scipy.signal import argrelmax, stft, peak_widths, welch, hilbert
from scipy.signal.windows import gaussian
from scipy.optimize import curve_fit
import ruptures as rpt


debug = False
changepointDetection = False

def square_wave(x, a, b, p):
    level = np.random.choice([0, 1], size=len(x), p=[0.5 * (1 - p), 0.5 * (1 + p)])
    return a + b * level

def model_func(x, a, b, p):
    return square_wave(x, a, b, p)

                                                    
def inport(fileLoc):
    data = pd.DataFrame(pd.read_feather(fileLoc))                                      # import function to pull in .feather files (binary)
    return data

fileLoc = "~\\skywaterTemp\\"
data = inport(fileLoc + 'RTS_B2_100nA82.feather')
grouped = data.groupby(data.Column)                                                     # group the data by the column "Column"

# print(data)
# for j in range(2,21):
for i in range(65,96):
    rollingD = pd.DataFrame(data=[],columns=['sig','stdev'], index=[])
    # rowRX = re.sub(r'[0-9]+$',
    #                 lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
    #                 str(j))  
    colRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the col number
                    str(i))  
    data2 = grouped.get_group(str(colRX)).reset_index(drop=True)                                           # gets the group with the specified column number
    # group = data1.groupby(data.Row)                                                 # group the data with the specified col # by column "Row"
    # data2 = group.get_group(str(rowRX)).reset_index(drop=True)                      # get the group with the spcified row number
    y,x = np.histogram(data2.Vgs, bins=50)                                          # make a histogram of the signal selected by grouping
    peak = find_peaks(y, distance=5, width=1, height=100)                           # find the peaks of the histogram
    XMAX = x[peak[0]]                                                               # find the X values of the peaks in histogram 
    YMAX = y[peak[0]]                                                               # find the Y values of the peaks in histogram
    size = 11                                                                       # window size of savgol_filter
    rollingD['sig'] = savgol_filter(data2.Vgs, window_length=10, polyorder=3)   
    sig = savgol_filter(data2.Vgs, window_length=size, polyorder=3)                 # filter the signal to reduce noise
    y1,x1 = np.histogram(sig, bins=50)                                              # make a histogram of filtered signal
    peaks = find_peaks(y1, width=1, height=100)                                     # find the peaks
    xmax = x1[peaks[0]]                                                             # find X values of peaks in hist
    ymax = y1[peaks[0]]                                                             # find Y values of peaks in hist

    if len(peaks[0]) >= 2:                                                          # determine if there is RTS by number of peaks in hist
        # for k in range(len(peaks[0])):
            # if y1[peaks[0][k]] == max(ymax):                                        # find the steadystate value of filtered signal
            #     # print(max(ymax))
            #     steadyS = k
        amplitude = x1[peaks[0]] - x1[peaks[0][0]]
        # amplitude = x1[peaks[0]] - x1[peaks[0][steadyS]]                            # find the rts amplitude for all rts levels
        amplitude = amplitude[amplitude != 0.]                                      # don't include zero
        windowSize = 20
        wSize = 10
        rollingD['stdev'] = rollingD.sig.rolling(10).std()
        # stdRolling['rolling'] = data2.Vgs.rolling(20).std()
        meanRolling = data2.Vgs.rolling(windowSize).mean()
        threshold = x1[peaks[0][0]] + rollingD.stdev*np.ones_like(rollingD.stdev)*3
        stdstdRolling = np.std(rollingD.stdev)
        # print(rollingD.stdev[20:])
        stdY, stdX = np.histogram(rollingD.stdev[windowSize:],bins='auto')
        stdHist_peaks , _= find_peaks(stdY, distance=40000)
        stdYmax = stdY[stdHist_peaks]
        stdXmax = stdX[stdHist_peaks]
        meanstdRolling = stdXmax[0] # np.mean(rollingD.stdev)
        print('peaks of rolling std histogram: ', stdHist_peaks)
        print('stdXmax: ', stdXmax[0])
        # plt.hist(rollingD.stdev[20:], bins='auto')
        # plt.plot(stdXmax, stdYmax, 'o')
        # plt.show()
        # for k in range(0, len(stdHist_peaks[0])):
        #     if stdY[stdHist_peaks[0][k]] == max(stdYmax):                                        # find the steadystate value of filtered signal
        #         # print(max(ymax))
        #         steadyS = k
        # print(stdXmax)
        sigma = meanstdRolling + stdstdRolling* 3
        stdPeaks = find_peaks(rollingD.stdev, height = sigma, distance=1, prominence=stdstdRolling)
        print('number of peaks in rolling std: ', len(stdPeaks[0]))
        if (len(stdPeaks[0])) < 25:
            certainty = 4
            wLength = 20
            wSize = 20
            peakWidths= 10
            pOrder = 4
        elif (len(stdPeaks[0])) < 100 and len(stdPeaks[0])>=25:
            certainty = 3
            wLength =75 # len(stdPeaks[0])
            wSize = 20
            peakWidths= 10
            pOrder = 4
        elif (len(stdPeaks[0])) < 200 and len(stdPeaks[0])>=100:
            certainty = 3
            wLength =50
            wSize = 20
            peakWidths= 1
            pOrder = 4
        elif (len(stdPeaks[0])) > 200:
            wLength = 11
            certainty = 2
            wSize = 20
            peakWidths= 1
            pOrder = 4
        else: 
            wSize = 10
            wLength = len(stdPeaks)
            certainty = 3
            peakWidths= 1
            pOrder = len(stdPeaks)- 1
        print(pOrder, ' ', wLength)
        rollingD['sig'] = savgol_filter(data2.Vgs, window_length=wLength, polyorder=pOrder)         
        rollingD['stdev'] = rollingD.sig.rolling(wSize).std()
        stdstdRolling = np.std(rollingD.stdev)
        print('Certainty: ', certainty)
        sigma = meanstdRolling + stdstdRolling* certainty        
        stdPeaks = find_peaks(rollingD.stdev, height = sigma, width=peakWidths, distance=10, prominence=stdstdRolling)
        print('number of peaks in rolling std: ', len(stdPeaks[0]))
        slope = pd.DataFrame(np.gradient(data2.Vgs), columns=['Slope'])
        slopeMean = np.mean(slope.Slope)
        sigmaS = slopeMean + np.std(slope.Slope) *4
        slopePeaks = find_peaks(np.abs(slope.Slope), height=sigmaS, prominence=np.std(slope.Slope))
        # print(slope)
        # analytic_signal = (hilbert(data2.Vgs))
        sigF = savgol_filter(data2.Vgs, window_length=11, polyorder=3)
        sigStd = np.std(sigF)
        sigMean = np.mean(sigF)
        sigSig = sigMean + sigStd
        if changepointDetection is True:
            start_Time = time.time()
            model = rpt.Window(width=20, model="l2", jump=5).fit(sigF)
            # model = rpt.BottomUp(model="l2", jump=2).fit(sigF)
            print('rolling std peaks: ' , (stdPeaks[0]))
            changePoints = model.predict(n_bkps=len(stdPeaks[0]), epsilon=3*200*sigStd**2, pen=np.log(100)*3*sigStd**2)
            endTime = time.time()
            processTime = endTime - start_Time
            print('Processing took: ', processTime)
            rpt.display(sigF, changePoints)
            print('Change points: ', changePoints)
            plt.show()
            plt.subplot(2,1,1)
            plt.plot(data2.Ticks, data2.Vgs)
            plt.plot(data2.Ticks, sigF)
            plt.plot(data2.Ticks[changePoints[:-1]], sigF[changePoints[:-1]], 'x')
            # plt.plot(data2.Ticks, np.ones_like(data2.Ticks)*sigSig)
            plt.subplot(2,1,2)
            plt.plot(data2.Ticks, sigF)
            plt.plot(data2.Ticks[stdPeaks[0]], sigF[stdPeaks[0]], 'x')
            plt.show()
        # stdPeaks = np.where(stdPeaks[0] > 0.0006)
        tau=pd.DataFrame(data=[], columns=['points','capture','state1', 'state2', 'state3', 'tau1', 'tau2', 'tau3'], index=[])
        # print(stdPeaks[0])
        wSi =int(wSize*.5)
        tau.points = stdPeaks[0]-wSi
        tau.capture = np.gradient(tau.points) #/2000
        plt.figure(figsize=(14,14))        
        # plt.subplot(2,1,1)
        # if len(amplitude) == 1:
        #     state1 = np.where(data2.Vgs[tau.points] <= np.mean(threshold))
        #     state2 = np.where(data2.Vgs[tau.points] > np.mean(threshold))
        #     tau.state1 = tau.points[state1[0]]
        #     tau.state2 = tau.points[state2[0]]
        #     tau.state1 = pd.notna(tau.state1)
        #     tau.state2 = pd.notna(tau.state2)
        #     tau.state1 = tau.state1.fillna(0)
        #     tau.state2 = tau.state2.fillna(0)
        #     tau.state1 = tau.state1.astype(int)
        #     tau.state2 = tau.state2.astype(int)
        #     tau.tau1 = tau.capture[tau.state1 == 1]/2000
        #     tau.tau2 = tau.capture[tau.state2 == 1]/2000
        #     plt.hist(tau.tau1, bins='auto', label='State 1')
        #     plt.hist(tau.tau2, bins='auto', label='State 2')
        #     # tau.tau3 = tau.capture[tau.state3 == 1]/2000
        #     # state3 = np.ones_like(data2.Vgs[tau.points]) * 
        # else: # len(amplitude<=2):
        #     state1 = np.where(data2.Vgs[tau.points] <= np.mean(threshold))
        #     state2 = np.where(data2.Vgs[tau.points] > np.mean(threshold))
        #     state3 = np.where(data2.Vgs[tau.points] >= np.mean(threshold)+np.std(data2.Vgs))
        # # print(state1, " ", state2) #, " ", state3)
        #     tau.state1 = tau.points[state1[0]]
        #     tau.state2 = tau.points[state2[0]]
        #     tau.state3 = tau.points[state3[0]]
        #     tau.state2 = tau.state2[tau.state2 != tau.state3]
        #     tau.state1 = pd.notna(tau.state1)
        #     tau.state2 = pd.notna(tau.state2)
        #     tau.state3 = pd.notna(tau.state3)
        #     tau.state1 = tau.state1.fillna(0)
        #     tau.state2 = tau.state2.fillna(0)
        #     tau.state3 = tau.state3.fillna(0)
        #     tau.state1 = tau.state1.astype(int)
        #     tau.state2 = tau.state2.astype(int)
        #     tau.state3 = tau.state3.astype(int)
        #     tau.tau1 = tau.capture[tau.state1 == 1]/2000
        #     tau.tau2 = tau.capture[tau.state2 == 1]/2000
        #     tau.tau3 = tau.capture[tau.state3 == 1]/2000 
        #     plt.hist(tau.tau1, bins='auto', label='State 1')
        #     plt.hist(tau.tau2, bins='auto', label='State 2')
        #     plt.hist(tau.tau3, bins='auto', label='State 3')
            
        # plt.show(block=True)    
        # plt.pause(5)
        # plt.close()
        stat = pd.DataFrame(data=[], index=[] , columns=['means'])
        stat.means=np.ones_like(tau.points)*np.mean(data2.Vgs)
        plt.subplot(2,1,1)

        for i in range(0, len(tau.points)-1):
            # print(stat.means)
            if i == 0:
                men = np.mean(data2.Vgs[0:tau.points[0]])
                stat.means[i]= men
                if stat.means[i] < np.mean(threshold): #*.99999:
                    color = 'orange'
                    tau.state1[i] = 1
                    tau.state2[i] = 0
                    tau.state3[i] = 0
                elif stat.means[i] >= np.mean(threshold) and stat.means[i] <= np.mean(threshold)+np.std(data2.Vgs):
                    color = 'blue'
                    print(stat.means[i])
                    tau.state1[i] = 0
                    tau.state2[i] = 1
                    tau.state3[i] = 0
                elif stat.means[i] > np.mean(threshold)+np.std(data2.Vgs) and len(amplitude) > 1:
                    color = 'red'
                    tau.state1[i] = 0
                    tau.state2[i] = 0
                    tau.state3[i] = 1 # )] pd.concat([stat.means,np.mean(data2.Vgs[0:tau.points[0]])], axis = 0, ignore_index=True)
                plt.plot(data2.Vgs[0:tau.points[0]], color=color)
                plt.plot(np.ones_like(data2.Vgs[0:tau.points[0]])*men)
            else:               #pd.concat([rtsData, vOut], axis = 0, ignore_index=True)  
                men = np.mean(data2.Vgs[tau.points[i-1]:tau.points[i]])
                stat.means[i] = men #pd.concat([stat.means, np.mean(data2.Vgs[tau.points[i-1]:tau.points[i]])]) #, axis = 0, ignore_index=True) #], axis = 0, ignore_index=True)
                
                sub = (np.mean(stat.means)-np.round(np.mean(stat.means), 3))
                equal = np.mean(data2.Vgs)*0.9999 #np.mean(stat.means)-sub*.1
                # print(np.mean(stat.means)-sub)
                # print(equal, 3)
                if stat.means[i] <= np.mean(threshold): #*.99999:
                    color = 'orange'
                    tau.state1[i] = 1
                    tau.state2[i] = 0
                    tau.state3[i] = 0
                elif (stat.means[i] > np.mean(threshold) and len(amplitude) == 1) or  (stat.means[i] > np.mean(threshold) and stat.means[i] <= np.mean(threshold)+np.std(data2.Vgs) and len(amplitude)>1):
                    color = 'blue'
                    tau.state1[i] = 0
                    tau.state2[i] = 1
                    tau.state3[i] = 0
                elif stat.means[i] > np.mean(threshold)+np.std(data2.Vgs) and len(amplitude) > 1:
                    color = 'red'
                    tau.state1[i] = 0
                    tau.state2[i] = 0
                    tau.state3[i] = 1
                plt.plot(data2.Vgs[tau.points[i-1]:tau.points[i]], color=color)
                plt.plot(np.ones_like(data2.Vgs[tau.points[i-1]:tau.points[i]])*men)
            # print(i,' ', mean) 

            # print((stat.means))
        print((tau))
        
        sub = (np.mean(stat.means)-np.round(np.mean(stat.means), 3))
        equal = np.mean(stat.means)-sub*.1
        print(threshold)
        plt.axhline(np.mean(threshold)) #*.99995)
        # plt.plot(np.ones_like(data2.Vgs)*threshold)
        plt.subplot(2,1,2)
        tau.tau1 = tau.capture[tau.state1 == 1]/2000
        tau.tau2 = tau.capture[tau.state2 == 1]/2000
        tau.tau3 = tau.capture[tau.state3 == 1]/2000
        plt.hist(tau.tau1, bins='auto', label='State 1')
        plt.hist(tau.tau2, bins='auto', label='State 2')
        # plt.hist(tau.tau3, bins='auto', label='state 3')

        # tau1 =pd.notna(tau.tau1)
        # print(tau1)
        # plt.hist(tau.tau1, bins='auto', label='State 1')
        # plt.hist(tau.tau2, bins='auto', label='State 2')
        # plt.hist(tau.tau3, bins='auto', label='State 3')
        # plt.plot(data2.Vgs[stat.means])
        plt.show(block=True)
        # plt.hist(tau.state1, bins='auto')
        # plt.show()
        print(tau)

        # for i in range(0, len(stdPeaks[0])-1):
        #     print(stdPeaks[0][i])
        #     tau['capture'] = stdPeaks[0][i] # stdPeaks[0][i+1] - stdPeaks[0][i]
        #     print(tau)

        plt.figure(figsize=(14,14))
        plt.subplot(2,1,1)
        plt.plot(data2.Ticks, data2.Vgs)
        plt.plot(data2.Ticks, rollingD.sig)
        plt.plot(data2.Ticks, np.ones_like(data2.Vgs)*np.mean(threshold))
        plt.plot(data2.Ticks, np.ones_like(data2.Vgs)*np.mean(threshold)+np.std(data2.Vgs))
        plt.plot(data2.Ticks, np.ones_like(data2.Vgs)*np.mean(threshold)+np.std(data2.Vgs)*2)
        wSize = wSize/2
        plt.plot(data2.Ticks[stdPeaks[0]-wSize], data2.Vgs[stdPeaks[0]-wSize], 'x', color='black')
        plt.plot(data2.Ticks[slopePeaks[0]], data2.Vgs[slopePeaks[0]], 'x', color='red')
        # plt.plot(data2.Ticks, analytic_signal)
        # plt.plot(data2.Ticks[])
        plt.subplot(2,1,2)
        plt.plot(data2.Ticks, np.abs(slope))
        plt.plot(data2.Ticks, rollingD.stdev)
        plt.plot(data2.Ticks, np.ones_like(data2.Ticks)*sigma, color='black')
        plt.plot(data2.Ticks, np.ones_like(data2.Ticks)*sigmaS)
        plt.plot(data2.Ticks, np.ones_like(data2.Ticks)*meanstdRolling, color='black')
        plt.plot(data2.Ticks[slopePeaks[0]], np.abs(slope.Slope[slopePeaks[0]]), 'x', color='red')
        plt.plot(data2.Ticks[stdPeaks[0]], (rollingD.stdev[stdPeaks[0]]), 'x', color='black')        
        if changepointDetection is False:
            plt.show(block=True)
            # plt.pause(3)
        else:
            plt.show(block=False)
        plt.close()
        # threshold = 1.026 + np.min(amplitude)*.9
        level1 = np.where(data2.Vgs < threshold)
        level2 = np.where(sig > threshold)
        # level1 = gaussian(sig, np.std(sig))
        # print(threshold)
        # print(level1[0])
        trial, _ = find_peaks(sig, distance=5, prominence=np.abs(min(amplitude)),      # find peaks of the filtered signal
                                rel_height=0.5)
        trial2, _ = find_peaks(-sig, distance=5, prominence=np.abs(min(amplitude)),    # find peaks of the negative filtered signal
                                rel_height=0.5)

        results_W, results_WH, results_ips, results_rps= peak_widths(sig,           # find the peak widths (capture time)
                                                                        trial, rel_height=0.5)
        results_NW, results_NWH, results_Nips, results_Nrps = peak_widths(-sig,     # find the valley widths (emission time)
                                                                            trial2, rel_height=0.5)
        
                                                                                    # capture and emission maybe flipped depending on signal
        # print(results_W)
        # print(results_W/2000)
        # if len(peaks[0]) == 4:
        #     data2.to_csv(fileLoc + 'csv\\' + '3levelRTS' + str(j) + str(i) + '.csv')
    else: 
        trial = []

    
#         # if rts is detected by a two or more order gaussian and has two or more transitions
    
    if len(trial) >= 2:
        # Plot some stuff 

        plt.figure(figsize=(14,14))
        plt.subplot(3, 1, 1)
        if debug is False:
            plt.plot(data2.Ticks, data2.Vgs, label='Vgs', color='gray')
            plt.plot(data2.Ticks, sig, label='Filtered Vgs', color='red')
            # plt.plot(data2.Ticks[trial], sig[trial], 'x', color='blue')
            plt.plot(data2.Ticks[level1[0]], sig[level1[0]], 'x', color='blue')
            plt.plot(data2.Ticks[level2[0]], sig[level2[0]], 'x', color='green')
            # plt.plot(data2.Ticks[trial2], sig[trial2], 'x', color='green')
            # plt.xlabel('Time (s)')
        else:
            plt.plot(data2.Vgs, label='Vgs', color='gray')
            plt.plot(sig, label='Filtered Vgs', color='red')
            plt.plot(trial, sig[trial], 'x', color='blue')
            plt.plot(trial2, sig[trial2], 'x', color='green')
            plt.hlines(results_WH, results_ips, results_rps, color="C2")
            # plt.xlabel("Data Points")
        plt.ylabel('Amplitude')
        plt.title('Vgs of row ' + str(82) + ' col '+ str(colRX))
        
        plt.legend()


        plt.subplot(3,2,3)

        frq, P1d = welch(data2.Vgs, fs=2000, window='hann', nperseg=20000,               #  Compute PSD using welch method
                            noverlap=None, nfft=20000)
        p1dSmooth = savgol_filter(P1d, window_length=5, polyorder=1)

        plt.yscale('log')
        plt.title('1/f Noise')
        plt.xscale('log')
        plt.plot(frq[5:], P1d[5:], color='gray')
        plt.plot(frq[5:], p1dSmooth[5:], color='red')

        plt.subplot(3, 2, 4)            
        plt.hist(data2.Vgs, bins=50, color='gray')
        plt.hist(sig, bins=50, color='red')
        plt.plot(xmax, ymax, 'o')
        plt.title('Rts amplitude ' + str(amplitude))

        plt.subplot(3, 2, 5)
        plt.hist(results_W/2000, bins=50, color='gray')
        meanTauE = np.mean(results_W)/2000
        plt.xlabel=("Time (Sec)")
        plt.title('Mean emission time (Sec): ' + str(meanTauE))

        plt.subplot(3, 2, 6)
        plt.hist((results_NW/2000), bins=50, color='gray')
        meanTauC = np.mean(results_NW)/2000
        plt.xlabel=("Time (Sec)")
        plt.title('Mean capture time: ' + str(meanTauC))

        plt.tight_layout()
        # plt.show()
        if changepointDetection is False:
            plt.show(block=False)
        else:
            plt.show(block=False)
        # plt.pause(8)
        plt.close()
        rollingD = rollingD.reset_index(drop=True, inplace=True)  

        # initial_guess = [0, 0, 0.1]  # Example initial guess for the parameters
        # optimized_params, _ = curve_fit(model_func, xdata=data2.Ticks, ydata=sig, p0=initial_guess)    
        # fitted_curve = model_func(data2.Ticks, *optimized_params)
        # plt.plot(data2.Ticks, fitted_curve, color='red', label='Fitted Curve')
        # plt.plot(data2.Ticks, data2.Vgs, label='Original Data')
        # # plt.xlabel('Time')
        # # plt.ylabel('Signal')
        # plt.legend()
        # plt.show()

     
