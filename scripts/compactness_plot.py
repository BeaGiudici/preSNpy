
########################################################
#
# Compute the comapctness for every model
#
########################################################

import os
import h5py
import numpy as np
import matplotlib.pyplot as plt

fig,ax = plt.figure()


for file in os.listdir('.'):
        if file.endswith('_presn'):
                print(file)
                MZAMS = file.replace('s','')
                MZAMS = float(MZAMS.replace('_pren',''))
                mbary, radius = np.genfromtxt(file, unpack=True, usecols=(1,2))
                idx = np.argmin(np.fabs(mbary - 2.5))
                r = radius / (1.e5)
                xi = 2.5 / (r/1000)
                plt.plot(MZAMS, xi, ls='', marker='.', color='red')
