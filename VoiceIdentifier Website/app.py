from flask import Flask, render_template, request, jsonify, Response
import librosa

import numpy as np
from scipy import signal
from scipy.fftpack import fft

from keras import backend as K

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout

import numpy as np 

from sklearn.utils import shuffle

import random

import tensorflow as tf
from keras.optimizers import *
from keras.layers import *
from keras.models import *
from keras.regularizers import l2

import keras
import csv
import random

import time
import os


INTERVAL = 400
STEP = 160

app = Flask(__name__)

SPEAKERS = ['Omkar Bhalerao', 'Amogh Bhalerao']

baselines = []

baselines.append(np.genfromtxt('spectrogram_0_1000.csv', delimiter=','))
baselines.append(np.genfromtxt('spectrogram_1_2125.csv', delimiter=','))

def get_siamese_model(input_shape):
    """
        Model architecture
    """
    
    # Define the tensors for the two input images
    left_input = Input(input_shape)
    right_input = Input(input_shape)
    
    # Convolutional Neural Network
    model = Sequential()
    model.add(Conv2D(64, (10,10), activation='relu', input_shape=input_shape,
                   kernel_initializer='random_normal', kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling2D())
    model.add(Conv2D(128, (7,7), activation='relu',
                     kernel_initializer='random_normal',
                     bias_initializer='random_normal', kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling2D())
    model.add(Conv2D(128, (4,4), activation='relu', kernel_initializer='random_normal',
                     bias_initializer='random_normal', kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling2D())
    model.add(Conv2D(256, (4,4), activation='relu', kernel_initializer='random_normal',
                     bias_initializer='random_normal', kernel_regularizer=l2(2e-4)))
    model.add(Flatten())
    model.add(Dense(4096, activation='sigmoid',
                   kernel_regularizer=l2(1e-3),
                   kernel_initializer='random_normal',bias_initializer='random_normal'))
    
    # Generate the encodings (feature vectors) for the two images
    encoded_l = model(left_input)
    encoded_r = model(right_input)
    
    # Add a customized layer to compute the absolute difference between the encodings
    L1_layer = Lambda(lambda tensors:K.abs(tensors[0] - tensors[1]))
    L1_distance = L1_layer([encoded_l, encoded_r])
    
    # Add a dense layer with a sigmoid unit to generate the similarity score
    prediction = Dense(1,activation='sigmoid',bias_initializer='random_normal')(L1_distance)
    
    # Connect the inputs with the outputs
    siamese_net = Model(inputs=[left_input,right_input],outputs=prediction)
    
    # return the model
    return siamese_net

def getResult(filename):
    global SPEAKERS
    K.clear_session()
    
    spectrograms = []
    
    rec, sr = librosa.load(filename, sr=16000)
    intervals = librosa.effects.split(rec,frame_length=640,hop_length=160)
    arrs = [rec[i[0]:i[1]] for i in intervals]
    newrec = np.concatenate(arrs)
    
    for idx in range(0, len(rec), sr):
        if(idx+sr < len(rec)):
            spectrogram = librosa.feature.melspectrogram(y=rec[idx:idx+sr], sr=sr, n_fft=INTERVAL, hop_length=STEP)
            spectrogram = spectrogram[:,:100]
            spectrograms.append(spectrogram)
    
    votes = np.zeros(len(SPEAKERS))
    
    if(len(spectrograms) == 0): return "Unknown"
    
    model = get_siamese_model(tuple(list(spectrograms[0].shape)+[1]))
    model.load_weights('epoch300-weights-new1.h5')

    for spec in spectrograms:
        testimage = np.asarray([spec[:,:]]*len(SPEAKERS)).reshape(len(SPEAKERS), spec.shape[0], spec.shape[1], 1)
        support_set = np.asarray(baselines).reshape(len(SPEAKERS), spec.shape[0], spec.shape[1], 1)
        probs = model.predict([testimage, support_set])
        votes[np.argmax(probs)]+=1
    
    return SPEAKERS[np.argmax(votes)]
    
    


@app.route('/messages', methods = ['POST'])
def api_message():
      # Open file and write binary (blob) data
      filename = "./file{}.wav".format(str(int(round(time.time()*1000))));
      f = open(filename, 'wb')
      f.write(request.data)
      f.close()
      speaker = getResult(filename)
      os.remove(filename)
      return jsonify({"speaker" : speaker})


@app.route('/')
def getHome():
    return render_template('index.html')
    
@app.route('/about')
def getAbout():
    return render_template('about_index.html')
    
@app.route('/record')
def getAudio():
    return render_template('audio_index.html')



if __name__ == '__main__':
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
