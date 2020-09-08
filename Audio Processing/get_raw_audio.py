import librosa

import soundfile as sf

import numpy as np
from scipy import signal
from scipy.fftpack import fft

from matplotlib import pyplot as plt
import os

INTERVAL = 640

import random


featurepath = "features.csv"

featurefile = open(featurepath, 'w')

f = [] #files go here


for index, filename in enumerate(f):
    rec, sr = librosa.load(filename, sr=16000)
    for x in range(0, len(rec), sr/2):
        if(x+(sr/2) < len(rec)):
            interval = rec[x:x+sr]
            featurefile.write(str(index))
            for i in interval:
                featurefile.write(","+str(i))
            featurefile.write("\n")





featurefile.close()


