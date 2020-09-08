import librosa

import soundfile as sf

import numpy as np
from scipy import signal
from scipy.fftpack import fft

from matplotlib import pyplot as plt

#VERY IMPORTANT: THESE ARE THE IDS I AM USING
ids = ['id02653', 'id00732', 'id03930', 'id00064','id00126','id08052','id07723','id07238','id01758','id09005']

import os

INTERVAL = 640

import random

path = "c:/Users/obhal/Documents/Senior Research/vox2_dev_aacaa/dev/aac/"

outfilepath = "c:/Users/obhal/Documents/Senior Research/training/"

featurepath = "features.csv"

featurefile = open(featurepath, 'w')

for index, idn in enumerate(ids):
    print(f"ID {idn} ({(index+1)}/{len(ids)}) starting.")
    print(index)
    newpath = path+idn
    dirs = [i[1] for i in os.walk(newpath)][0]
    count = 0
    for dir in dirs:
        newnewpath = newpath+"/"+dir
        for r, d, f in os.walk(newnewpath):
            for file in f:
                filename = r+"/"+file
                rec, sr = librosa.load(filename, sr=16000)
                intervals = librosa.effects.split(rec,frame_length=640,hop_length=160//4)
                arrs = [rec[i[0]:i[1]] for i in intervals]
                newrec = np.concatenate(arrs)
                zcr = librosa.feature.zero_crossing_rate(newrec, frame_length=640,hop_length=160)
                maxv = np.max(zcr)
                l = np.argwhere(zcr < 0.25*maxv)[:,1]*INTERVAL
                for idx in l:
                    currfile = rec[idx:idx+INTERVAL]
                    if(np.count_nonzero(currfile) < INTERVAL):
                        continue

                    frequencies, power_spectrum = signal.periodogram(currfile)

                    fourier_transform = (2.0/INTERVAL) * np.abs(fft(currfile))[0:INTERVAL//2]
                    fft_freqs = np.linspace(0.0, 1/(2*sr), INTERVAL//2)

                    '''plt.plot(fft_freqs, fourier_transform)
                    plt.show()'''

                    fft_peaks = signal.argrelmax(fourier_transform)[0]
                    nfftpeaks = [(fourier_transform[i], fft_freqs[i], i) for i in fft_peaks][:20]
                    #nfftpeaks = sorted([(fourier_transform[i], fft_freqs[i], i) for i in fft_peaks])[-1:-11:-1]

                    peaks = signal.argrelmax(power_spectrum)[0]
                    npeaks = [(power_spectrum[i], frequencies[i], i) for i in peaks][:20]
                    #npeaks = sorted([(power_spectrum[i], frequencies[i], i) for i in peaks])[-1:-11:-1]


                    featurefile.write(str(index)+','+ ','.join(f"{i[1]}" for i in sorted((j[2], j[0]) for j in npeaks))+ ',' + ','.join(f"{i[1]}" for i in sorted((j[2], j[0]) for j in nfftpeaks)) + "\n")



        count+=1
        print(f"{count}/{len(dirs)} directories done.")
    print(f"ID {idn} done.")

featurefile.close()


