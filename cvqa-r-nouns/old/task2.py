import sys
import argparse
from gensim import *
import numpy as np
import json
import os
import time

from keras.models import Sequential
from keras.layers import Dense,Activation, Dropout
from keras.layers import Merge, LSTM, Dense
from keras.optimizers import *

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

maxQuestionLength = 20
numberOfEpochs = 15
excludeWords = ['a','the','what','that','to','who','why']

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(os.path.join(filename)) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

def extractSentenceFeatures(w2v, sentence):
	# print 'Extracting features for [%s]' % (sentence)
	words=sentence.split(' ')
	features=np.zeros((maxQuestionLength,300))
	selected = []
	wordIndex=0
	for word in words:
		selectedValue = False
		if word in w2v:
			if not(word.lower() in excludeWords):
				features[wordIndex]=w2v[word]
				wordIndex+=1
				selectedValue = True

		selected.append(selectedValue)
	return np.asarray(features), selected

def extractFeatures(w2v, questions, image_captions):
	questionNumber = 0
	question_features=[]
	caption_features=[]
	applicable_labels=[]
	totalQuestions = len(questions)
	for i,questionIndex in enumerate(questions):
		questionNumber += 1
		print "---- [%d/%d] ----" % (questionNumber,totalQuestions)
		s = questions[questionIndex]
		if (len(s['label']) > maxQuestionLength):
			print 'Skipping question: [%s] Label length: [%d]' % (s['question'], len(s['label']))
			continue
		filename = s['image']

		# #print "Generating Question_features..."
		ques_features, selected = extractSentenceFeatures(w2v, s['question'])

		#print "Generating Caption_features..."
		cap_features, _ = extractSentenceFeatures(w2v, image_captions[filename])

		label=np.zeros(maxQuestionLength)

		print 'Label: [%s] Length: [%d]' % (s['label'], len(s['label']))

		li = 0
		for l in s['label'].split(' '):
			if (selected[li]):
				label[li] = int(l)
				li += 1

		label = np.asarray(label)

		question_features.append(ques_features)
		caption_features.append(cap_features)
		applicable_labels.append(label)

	question_features=np.asarray(question_features)
	caption_features=np.asarray(caption_features)
	applicable_labels=np.asarray(applicable_labels)
	# print 'question_features shape'
	# print question_features.shape
	# print 'caption_features shape'
	# print caption_features.shape
	# print 'label shape'
	# print applicable_labels.shape
	return question_features, caption_features, applicable_labels

def parse_args():
	parser= argparse.ArgumentParser(description='Train/Test CVQA Models')
	parser.add_argument('-w','--word2VecPath', help='Word2Vec model file')
	parser.add_argument('-x','--captionFile', help='Input caption file')
	parser.add_argument('-q','--questionsFile', help='Input questions file')
	parser.add_argument('-s','--sampleSize', help='Number of images to sample. Use 0 for all images',type=int)

	if len(sys.argv) ==1:
		parser.print_help()
		sys.exit(1)

	args=parser.parse_args()
	return args

def train_model_lstm(X_train_ques, X_train_cap, y_train, loadWeights=None):
	data_dim = 300
	timesteps = 20
	nb_classes = maxQuestionLength
	print "Defining Architecture..."
	encoder_a = Sequential()
	encoder_a.add(LSTM(40, input_shape=(timesteps,data_dim)))
	#encoder_a.add(LSTM(40))

	encoder_b = Sequential()
	encoder_b.add(LSTM(40, input_shape=(timesteps,data_dim)))
	#encoder_b.add(LSTM(40))

	decoder = Sequential()
	decoder.add(Merge([encoder_a, encoder_b], mode='concat'))
	decoder.add(Dense(40, activation='relu'))
	decoder.add(Dense(20, activation='relu'))
	decoder.add(Dense(nb_classes, activation='sigmoid'))

	decoder.compile(loss='binary_crossentropy', optimizer='rmsprop')
	print "Architecture Defined..."

	X_train_ques=np.asarray(X_train_ques)
	X_train_cap=np.asarray(X_train_cap)
	y_train=np.asarray(y_train)
	
	if loadWeights!=None:
		decoder.load_weights(loadWeights)
	else:
		print "Fitting model..."
		'''
		for epoch in range(1,3):
			for i in range(0,len(X_train_ques)):
				decoder.fit([np.asarray([X_train_ques[i]]), np.asarray([X_train_cap[i]])], np.asarray([y_train[i]]), nb_epoch=1)
		'''
		decoder.fit([X_train_ques,X_train_cap], y_train, nb_epoch=numberOfEpochs)
	
	return decoder

def test_model_lstm(X_test_ques, X_test_cap, y_test, model):

	X_test_ques=np.asarray(X_test_ques)
	X_test_cap=np.asarray(X_test_cap)
	y_test=np.asarray(y_test)
	
	pred=model.predict_proba([X_test_ques, X_test_cap])
	thresh=0.15
	pred_labels=pred>thresh
	gt_labels=np.asarray(y_test)>0.5
	pred_labels_n=pred<thresh
	gt_labels_n=np.asarray(y_test)<0.5

	return pred_labels,gt_labels,pred_labels_n,gt_labels_n

def stats(pred, gt, pred_n, gt_n):
	stats = {}
	#	print accuracy_score(gt,pred)
	stats['True Premise Recall'] = recall_score(gt,pred, average='micro')
	stats['True Premise Precision'] = precision_score(gt,pred, average='micro')
	stats['False Premise Recall'] = recall_score(gt_n,pred_n, average='micro')
	stats['False Premise Precision'] = precision_score(gt_n,pred_n, average='micro')
	stats['Normalized Accuracy'] = (recall_score(gt,pred, average='micro')+recall_score(gt_n,pred_n, average='micro'))/2

	print "Relevant Class Recall: "+str(recall_score(gt,pred, average='micro'))
	print "Relevant Class Precision: "+str(precision_score(gt,pred, average='micro'))

	#	print accuracy_score(gt_n,pred_n)
	print "Irrelevant Class Recall: "+str(recall_score(gt_n,pred_n, average='micro'))
	print "Irrelevant Class Precision: "+str(precision_score(gt_n,pred_n, average='micro'))
	print "Normalized Acc: mean(Recall_Relevant_Class, Recall_Irrelevant_Class) : "
	print (recall_score(gt,pred, average='micro')+recall_score(gt_n,pred_n, average='micro'))/2

	return stats

if __name__=='__main__':
	args = parse_args()
	tic = time.time()

	print "Loading Word2Vec Dictionary. This may take a long time..."
	w2v=models.Word2Vec.load_word2vec_format(args.word2VecPath, binary=True)

	print "Loading Captions generated by a Pre-Trained Captioning Model for Images..."
	image_captions = readJson(args.captionFile)

	print "Loading Questions..."
	questions = readJson(args.questionsFile)

	print "Extracting Features ... " 
	question_features, caption_features, labels = extractFeatures(w2v, questions, image_captions)

	split = len(question_features) * 2/3
	X_train_ques=question_features[:split]
	X_train_cap=caption_features[:split]
	y_train= labels[:split]

	X_test_ques=question_features[split+1:]
	X_test_cap=caption_features[split+1:]
	y_test= labels[split+1:]

	model=train_model_lstm(X_train_ques, X_train_cap, y_train)	

	print "Testing on Train..."
	pred,gt,pred_n,gt_n=test_model_lstm(X_train_ques, X_train_cap, y_train ,model)

	outputStats = {}
	outputStats['train'] = stats(pred,gt,pred_n,gt_n)	

	print "Testing on Test..."
	pred,gt,pred_n,gt_n=test_model_lstm(X_test_ques, X_test_cap, y_test ,model)	
	outputStats['test'] = stats(pred,gt,pred_n,gt_n)
	
	print 'Finished in (t=%0.2fs)'%(time.time()- tic)
