import numpy as np

from keras.models import Sequential
from keras.layers import Dense,Activation, Dropout
from keras.layers import Merge, LSTM, Dense
from keras.optimizers import *

class_weight = {0 : 1., 1: 1.}

class RandomModel:
	def init(self):
		pass

	def train(self, args, trainData, loadWeights=None):
		return {}

	def test(self,testData, model):
		y_test = testData['y']
		pred = np.random.rand(y_test.shape[0],1)
		thresh=0.15
		pred_labels=pred>thresh
		gt_labels=np.asarray(y_test)>0.5
		pred_labels_n=pred<thresh
		gt_labels_n=np.asarray(y_test)<0.5

		return pred_labels,gt_labels,pred_labels_n,gt_labels_n, pred

class MLP:
	def __init__(self, data_dims):
		self.data_dims = data_dims

	def train(self, args, trainData, loadWeights=None):
		model=Sequential()
		model.add(Dense(200,input_dim=self.data_dims,activation='relu'))
		model.add(Dense(150,activation='relu'))
		model.add(Dense(80,activation='relu'))
		model.add(Dense(1,activation='sigmoid'))

		model.compile(loss='binary_crossentropy',optimizer='adadelta')

		X_train = trainData['X']
		y_train = trainData['y']

	#	print len(X_train)
	#	print len(y_train)

		if loadWeights!=None:
			print "Loading Pretrained Weights..."
			model.load_weights(loadWeights) #600in,200,150,10,1
		else:
			print "Training Model..."
			model.fit(X_train,y_train, nb_epoch=args.numberOfEpochs, class_weight=class_weight)
		return model

	def test(self,testData, model):
		X_test = testData['X']
		y_test = testData['y']
		pred=model.predict_proba(X_test)
		thresh=0.15
		pred_labels=pred>thresh
		gt_labels=np.asarray(y_test)>0.5
		pred_labels_n=pred<thresh
		gt_labels_n=np.asarray(y_test)<0.5

		return pred_labels,gt_labels,pred_labels_n,gt_labels_n, pred

class QuestionOnlyLSTMModel:
	def init(self):
		pass

	def train(self, args, trainData, loadWeights=None):
		data_dim = 300
		timesteps = 20
		nb_classes = 1

		print "Defining Architecture..."
		encoder_a = Sequential()
		encoder_a.add(LSTM(40, input_shape=(args.windowSize,data_dim)))

		decoder = Sequential()
		decoder.add(encoder_a)
		decoder.add(Dense(40, activation='relu'))
		decoder.add(Dense(20, activation='relu'))
		decoder.add(Dense(nb_classes, activation='sigmoid'))

		decoder.compile(loss='binary_crossentropy', optimizer='rmsprop')
		print "Architecture Defined..."

		X_train_ques = trainData['X']
		y_train = trainData['y']
		X_train_ques=np.asarray(X_train_ques)
		y_train=np.asarray(y_train)
		
		if loadWeights!=None:
			decoder.load_weights(loadWeights)
		else:
			print "Fitting model..."
			decoder.fit(X_train_ques, y_train, nb_epoch=args.numberOfEpochs, class_weight = class_weight)
		
		return decoder

	def test(self,testData, model):
		X_test_ques = testData['X']
		y_test = testData['y']

		X_test_ques=np.asarray(X_test_ques)
		y_test=np.asarray(y_test)
		
		pred=model.predict_proba(X_test_ques)
		thresh=0.15
		pred_labels=pred>thresh
		gt_labels=np.asarray(y_test)>0.5
		pred_labels_n=pred<thresh
		gt_labels_n=np.asarray(y_test)<0.5

		return pred_labels,gt_labels,pred_labels_n,gt_labels_n, pred

class LSTMModel:
	def init(self):
		pass

	def train(self, args, trainData, loadWeights=None):
		data_dim = 300
		timesteps = 20
		nb_classes = 1
		print "Defining Architecture..."
		encoder_a = Sequential()
		encoder_a.add(LSTM(40, input_shape=(args.windowSize,data_dim)))
		#encoder_a.add(LSTM(40))

		encoder_b = Sequential()
		encoder_b.add(LSTM(40, input_shape=(timesteps,data_dim)))
		
		decoder = Sequential()
		decoder.add(Merge([encoder_a, encoder_b], mode='concat'))
		decoder.add(Dense(40, activation='relu'))
		decoder.add(Dense(20, activation='relu'))
		decoder.add(Dense(nb_classes, activation='sigmoid'))

		decoder.compile(loss='binary_crossentropy', optimizer='rmsprop')
		print "Architecture Defined..."

		X_train_ques = trainData['X']
		X_train_cap = trainData['X_cap']
		y_train = trainData['y']
		X_train_ques=np.asarray(X_train_ques)
		X_train_cap=np.asarray(X_train_cap)
		y_train=np.asarray(y_train)
		
		if loadWeights!=None:
			decoder.load_weights(loadWeights)
		else:
			print "Fitting model..."
			decoder.fit([X_train_ques,X_train_cap], y_train, nb_epoch=args.numberOfEpochs, class_weight = class_weight)
		
		return decoder

	def test(self,testData, model):
		X_test_ques = testData['X']
		X_test_cap = testData['X_cap']
		y_test = testData['y']

		X_test_ques=np.asarray(X_test_ques)
		X_test_cap=np.asarray(X_test_cap)
		y_test=np.asarray(y_test)
		
		pred=model.predict_proba([X_test_ques, X_test_cap])
		thresh=0.15
		pred_labels=pred>thresh
		gt_labels=np.asarray(y_test)>0.5
		pred_labels_n=pred<thresh
		gt_labels_n=np.asarray(y_test)<0.5

		return pred_labels,gt_labels,pred_labels_n,gt_labels_n, pred