import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import poisson

fileLoc = 'D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\'

def stemPlt():
    dtList = [0,1,2,3,6,-4,-8,0,0]
    k=[-1,0,1,2,3,4,5,6,7]
    # dtList1 = [6,2,1,1,1,1,2,2]
    # k1=[1,3,5,7,9,11,13,15]
    markerline, stemlines, basline = plt.stem(k, dtList, linefmt = 'teal', markerfmt='o')
    # markerline1, stemlines1, basline1 = plt.stem(k1, dtList1, linefmt = 'teal', markerfmt='o')
    # markerline1.set_markerfacecolor('none')
    plt.show()

def boxWalk(p,L,N):
    X = np.zeros((N,1))
    for n in range(2, N):
        if X[n-1]==0:
            X[n] = 1
        elif X[n-1] == L:
            X[n] = L-1
        else:
            if np.random.rand() < p:
                X[n] = X[n-1] - 1
            else:
                X[n] = X[n-1] + 1
    # print(X)
    return X

def hw2():
    p = 0.5;                            # probability of moving left
    L = 25;                             # box length
    N = 500;                            # run time
    M = 2000;                           # number of sample paths 
    X1 = pd.DataFrame(data=[], index=[], columns=[]) 
    for m in range(1, M):
        X = pd.DataFrame(boxWalk(p, L, N))
        X1 = pd.concat([X1, X], axis=1)

    meanpath = np.mean(X1, axis=1)
    stdpath = np.std(X1, axis=1)
    meanplus = meanpath + stdpath
    meanminus = meanpath - stdpath

    timeax = np.linspace(1, N, N)

    plt.plot(timeax, X1.iloc[:, :4])
    plt.xlabel('Time, N')
    plt.ylabel('Statistics of X[N]')
    plt.axis([1, N, 0, L])
    plt.legend(['sample path 1', 'sample path 2', 'sample path 3','sample path 4'])
    plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw2\\p2.png')
    fig1 = plt.show(block=False)
    plt.pause(3)
    plt.close(fig1)

    plt.plot(timeax, meanpath)
    plt.plot(timeax, meanplus)
    plt.plot(timeax, meanminus)
    plt.legend(['mean', 'upper bound', 'lower bound'])
    plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw2\\p3.png')
    fig2 = plt.show(block=False)
    plt.pause(3)
    plt.close(fig2)


    power = np.linspace(0,3,4, dtype=int)
    # times = 35 * 2**power
    times = [1, 100, 300, 450]
    for i in range(1,5,1):
        t = times[i-1]
        plt.subplot(2,2,i)
        plt.hist(X1.iloc[:,[t]], bins=list(range(0, L)))
        plt.ylabel('Histogram at time ' + str(t))
    # plt.axis([-1, L+1, 0, 20])
    plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw2\\p4.png')
    fig3 = plt.show(block=False)
    plt.pause(3)
    plt.close(fig3)

def possionProcess(n):
    lambdaa = 0.1
    t = 10
    p = (lambdaa * t) / n
    N = pd.DataFrame(data=[], index=[0], columns=[])
    b = pd.DataFrame(data=[], index=[], columns=[])

    for i in range(10000):
        b = np.sum((np.random.rand(1,n) < p))
        N[i] = b 
    return N

def RTW(p,N):
    x = np.random.rand(N)
    # rtw = pd.DataFrame(data=[],index=[],columns=[])
    rtw = np.zeros((N,1))
    for i in range(N):
        if x[i] < p:
            rtw[i] = 1
        else:
            rtw[i] = -1
    return rtw
    

def Hw3_1():
    N = pd.DataFrame(data=[], index=[], columns=[])
    j=0
    for i in range(2,14,2):
        N = pd.concat([N,possionProcess(i)], ignore_index=True)
    for j in range(0,6,1):
        plt.subplot(2,3,j+1)
        plt.hist(N.iloc[j])
        plt.semilogy()
        i = list(range(2,14,2))
        plt.ylabel('Histogram with  ' + str(i[j]) + ' subintervals')
    plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw3\\p1.png')
    plt.show()
    for i in range(2,14,2):
        possionDistribution = poisson.rvs(1, size = i)
        print(possionDistribution)
        plt.subplot(2,3,j+1)
        j=j+1
        print(j)
        plt.hist(possionDistribution, density=True)
        plt.semilogy()
        plt.title("alpha = 1")
        # i = list(range(2,14,2))
        plt.ylabel('Histogram with  ' + str(i) + ' subintervals')
    plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw3\\p1.1.png')
    plt.show()

def Hw3_2():
    rtw1 = pd.DataFrame(data=[],index=[],columns=[])
    meanpath = pd.DataFrame(data=[],index=[],columns=[])
    varpath = pd.DataFrame(data=[],index=[],columns=[])
    p = 0.5
    N = 25
    M = 10
    for i in range(M):
        rtw = pd.DataFrame(RTW(p, N))
        rtw1 = pd.concat([rtw1, rtw], axis =1, ignore_index=True)
    fig1 = rtw1.plot(drawstyle='steps', subplots=True,
                      ylabel='X[N]', sharex=True, sharey=True, figsize=(12,8)) 
    # plt.subplot(2,3,1)
    plt.savefig(fileLoc + 'hw3\\p1.png')
    plt.xlabel('Time (Sec)')
    # plt.ylabel('RTW of X[N]')
    plt.show(block = False)
    plt.pause(1)
    plt.close()
    # plt.subplot(2,3,2)
    meanpath = rtw1.mean().transpose()
    # meanpath = meanpath.transpose()
    print(meanpath)
    # for i in range(len(meanpath)):
    #     col = (np.random.random(), np.random.random(), np.random.random())
    #     plt.axhline(y = meanpath[i], label='meanpath ' + str(i), c=col)
    plt.subplot(2,1,1)
    plt.plot(meanpath)
    plt.xlabel('Time (Sec)')
    plt.ylabel('Mean of X[N]')
    plt.savefig(fileLoc + 'hw3\\p2_1.png')
    varpath = rtw1.std()
    plt.subplot(2,1,2)
    plt.plot(varpath)
    plt.xlabel('Time (Sec)')
    plt.ylabel('Var of X[N]')
    plt.savefig(fileLoc + 'hw3\\p2_2.png')
    plt.show(block = False)
    plt.pause(1)

# Hw3_2() 
def babysitting(M,N,pL, pR):
    square=np.linspace(4,4,num=N+1)
    Square = pd.DataFrame(data=[], index=[], columns=[])
    for m in range(M):
        for n in range(N):
            prob = np.random.rand(1)
            # print(prob)
            if square[n] == 7:
                square[n+1]= 4
            elif square[n] == 1:
                square[n+1] = 4
            elif pR > prob and square[n] <=6:
                square[n+1] = square[n] + 1
            elif pL < prob and square[n] >=2:
                square[n+1] = square[n] - 1
            else:
                # if square[n-1] - square[n] < 0:
                #     advance = -1
                # else: # square[n-1] - square[n] > 0:
                #     advance = 1

                # print(advance)
                square[n+1]=square[n]
        Square[m] = square
        # print(square)
    return Square
def hw5_1():
    pL = 0.5
    pR = 0.3
    pS = 0.2
    N = 50
    square = babysitting(4,N,pL,pR)
    print(square)

    P = np.array([[0, 0, 0, 1, 0, 0, 0],
                [0.5, 0.2, 0.3, 0, 0, 0, 0],
                [0, 0.5, 0.2, 0.3, 0, 0, 0],
                [0, 0, 0.5, 0.2, 0.3, 0, 0],
                [0, 0, 0, 0.5, 0.2, 0.3, 0],
                [0, 0, 0, 0, 0.5, 0.2, 0.3,],
                [0, 0, 0, 1, 0, 0, 0]])
    eig_vals, eig_vecs = np.linalg.eig(P.T)

    # find the index of the eigenvalue of 1
    idx = np.where(np.isclose(eig_vals, 1))[0]

    if idx.size > 0:
        # extract the corresponding eigenvector
        pi = eig_vecs[:, idx[0]].real
        # normalize the eigenvector to obtain the steady state PMF
        pi = pi / np.sum(pi)
        print("Steady state PMF:", pi)
    else:
        print("No steady state exists.")

def hw6():
    # Parameters
    lambda_val = 2.0   # arrival rate
    mu_val = 3.0       # departure rate
    delta_t = 0.01     # time interval width
    total_intervals = 1000   # total number of intervals
    total_time = total_intervals * delta_t   # total simulation time
    num_runs = 1000    # number of simulation runs

    # Initialization
    state_avg = np.zeros(total_intervals)   # average state of the queue
    n_avg = np.zeros(num_runs)   # final number of customers in the queue for each run

    # Simulation
    for r in range(num_runs):
        state = np.zeros(total_intervals)   # state of the queue for each run
        n = 0    # number of customers in the queue at t=0

        for i in range(total_intervals):
            # Compute probabilities
            p_arrival = lambda_val * delta_t
            p_departure = mu_val * delta_t
            
            # Update state
            if n == 0:
                state[i] = np.random.binomial(1, p_arrival)   # no customers in queue
            else:
                state[i] = state[i-1] + np.random.binomial(1, p_arrival) - np.random.binomial(1, p_departure)
            
            n = state[i]

        n_avg[r] = state[-1]   # final number of customers in the queue for each run
        state_avg += state / num_runs   # average state of the queue over all runs

    # Print the average state at each time interval
    for i in range(total_intervals):
        print(f"t = {i*delta_t:.2f}s: N(t) = {state_avg[i]}")

    # Print the average final number of customers in the queue over all runs
    print(f"Average final number of customers in the queue: {np.mean(n_avg)}")
    print(f"Thoretical final number of customers in the queue: {lambda_val/(mu_val-lambda_val)}")
