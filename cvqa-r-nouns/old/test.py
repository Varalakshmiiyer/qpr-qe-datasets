from keras.models import Sequential
import numpy as np
from keras.models import *
from keras.layers import *
import keras

n_in = 684
n_out = 684
n_hidden = 512
n_samples = 2297
n_timesteps = 87

model = Sequential()
model.add(GRU(n_hidden, return_sequences=True, input_shape=(n_timesteps, n_in)))
model.add(TimeDistributed(Dense(n_out)))
model.compile(loss='mse', optimizer='rmsprop')

X = np.random.random((n_samples, n_timesteps, n_in))
Y = np.random.random((n_samples, n_timesteps, n_out))

Xp = model.predict_proba(X)
print Xp.shape
print Y.shape

model.fit(X, Y, nb_epoch=1)