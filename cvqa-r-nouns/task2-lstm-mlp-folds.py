import os
from gensim import models
import json
import numpy as np
from keras.models import *
from keras.layers import *
import keras
from sklearn.metrics import *
import keras.backend as K
import pandas as pd
import argparse

pd.options.mode.chained_assignment = None

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(filename) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData


def filterWords(questionRow, caption):
	labels = [int(l) for l in questionRow['wordLabels'].split(' ')]
	questionWords = questionRow['question'].split(' ')
	captionWords = caption.split(' ')

	newLabels = []
	newQuestionWords = []
	newCaptionWords = []
	for wi, w in enumerate(questionWords):
		if w in w2v:
			if w.lower() not in excludeWordList:
				newQuestionWords.append(w)
				newLabels.append(labels[wi])
	for w in captionWords:
		if w in w2v:
			if w.lower() not in excludeWordList:
				newCaptionWords.append(w)

	return newLabels, newQuestionWords, newCaptionWords

def extractBowFeatures(questionRows, totalLength, maxLength):
	X = []
	y = []

	for i,questionRow in questionRows.iterrows():
		imageFilename = questionRow['image']
		caption = imageCaptions[imageFilename]

		labels, questionWords, captionWords = filterWords(questionRow, caption)

		feature = np.zeros(len(word_index))
		feature1 = np.zeros(len(word_index))
		labelFeature = np.zeros(len(word_index))

		relevant = True
		for li,l in enumerate(labels):
			if (l == 0):
				labelFeature[word_index[questionWords[li]]] = 1
				relevant = False

		if relevant:
			labelFeature[0] = 1
		
		for ci,c in enumerate(captionWords):
			feature[word_index[c]] += 1
			# feature[word_index[c]] = max(feature[word_index[c]], 1)

		for ci,c in enumerate(questionWords):
			feature[word_index[c]] += 1
			# feature1[word_index[c]] = max(feature1[word_index[c]], 1)

		# feature = feature1 + feature


		X.append(feature)
		y.append(labelFeature)

	return np.asarray(X),np.asarray(y)

def extractFeatures(questionRows, totalLength, maxLength):

	# print '\tTotal Question Rows: [%d]' % (len(questionRows))

	X_captions = []
	x_questions = []
	y = []

	for i,questionRow in questionRows.iterrows():
		imageFilename = questionRow['image']
		caption = imageCaptions[imageFilename]

		labels, questionWords, captionWords = filterWords(questionRow, caption)

		captionFeature = np.zeros((maxLength, wordVectorSize))
		questionFeature = np.zeros((maxLength, wordVectorSize))
		labelFeature = np.zeros(len(word_index))

		relevant = True
		for li,l in enumerate(labels):
			if (l == 0):
				labelFeature[word_index[questionWords[li]]] = 1
				relevant = False

		if relevant:
			labelFeature[0] = 1
		
		for ci,c in enumerate(captionWords):
			captionFeature[ci] = w2v[c]

		for ci,c in enumerate(questionWords):
			questionFeature[ci] = w2v[c]

		X_captions.append(captionFeature)
		x_questions.append(questionFeature)
		y.append(labelFeature)

	return np.asarray(x_questions),np.asarray(X_captions),np.asarray(y)
 
def extractAvgFeatures(questionRows, totalLength, maxLength):

	# print '\tTotal Question Rows: [%d]' % (len(questionRows))

	X = []
	y = []

	for i,questionRow in questionRows.iterrows():
		imageFilename = questionRow['image']
		caption = imageCaptions[imageFilename]

		labels, questionWords, captionWords = filterWords(questionRow, caption)

		captionFeature = []
		questionFeature = []
		labelFeature = np.zeros(len(word_index))

		relevant = True
		for li,l in enumerate(labels):
			if (l == 0):
				labelFeature[word_index[questionWords[li]]] = 1
				relevant = False

		if relevant:
			labelFeature[0] = 1
		
		for ci,c in enumerate(captionWords):
			captionFeature.append(w2v[c])

		for ci,c in enumerate(questionWords):
			questionFeature.append(w2v[c])

		captionFeature=sum(captionFeature)/float(len(captionFeature))
		questionFeature=sum(questionFeature)/float(len(questionFeature))
		X.append(np.concatenate((questionFeature,captionFeature),0))
		y.append(labelFeature)

	return np.asarray(X),np.asarray(y)

def extractVocab(rowSet):
	word_index = {'RELEVANT':0}
	index_word = {0:'RELEVANT'}
	for r in rowSet:
		for i,questionRow in r.iterrows():
			imageFilename = questionRow['image']
			caption = imageCaptions[imageFilename]

			questionWords = questionRow['question'].split(' ')
			for w in questionWords:
				if (w in w2v) and (w not in word_index) and (w not in excludeWordList):
					word_index[w] = len(word_index)
					index_word[word_index[w]] = w
			captionWords = caption.split(' ')
			for w in captionWords:
				if (w in w2v) and (w not in word_index) and (w not in excludeWordList):
					word_index[w] = len(word_index)
					index_word[word_index[w]] = w

	return word_index, index_word


parser = argparse.ArgumentParser()
parser.add_argument('-d', action='store', dest='dataFile', help='Data file')
parser.add_argument('-o', action='store', dest='outputPath', help='Output path')
parser.add_argument('-e', action='store', dest='numberOfEpochs', help='Epochs', type=int)
parser.add_argument('-f', action='store', dest='numberOfFolds', help='Folds', type=int)
parser.add_argument('-b', action='store', dest='baseDataDirectory', help='Base directory')

results = parser.parse_args()

# modelTypes = {'all-bidirect':50, 'all':50, 'bow':50,'capOnly':5,'quesOnly':5}

# modelTypes = ['all-bidirect','all','avg','bow']

modelTypes = ['capOnly', 'quesOnly']

dataFile = results.dataFile
numberOfEpochs = results.numberOfEpochs
numberOfFolds = results.numberOfFolds
baseDataDirectory = results.baseDataDirectory

word2VecPath = os.path.join(baseDataDirectory, 'word2vec/google-news/GoogleNews-vectors-negative300.bin')
captionFile = os.path.join(baseDataDirectory, 'cvqa/imagecaptions.json')

wordVectorSize = 300
maxLength = 20
totalLength = maxLength * 2
excludeWordList = ['is','a','the','what','that','to','who','why']

print "Loading Word2Vec Dictionary. This may take a long time..."
w2v = models.Word2Vec.load_word2vec_format(word2VecPath, binary=True)

print "Loading Captions generated by a Pre-Trained Captioning Model for Images..."
imageCaptions = readJson(captionFile)

print "Loading Questions..."

allRows = pd.read_csv(dataFile)

print '\tAll rows: [%d]' % (len(allRows))

print "Removing Questions Without Matching Captions..."

allRows = allRows[allRows['image'].isin(imageCaptions)]

print '\tAll rows: [%d]' % (len(allRows))

print "Extracting Vocab..."

word_index, index_word = extractVocab([allRows])

print 'Vocab size: [%d]' % (len(word_index))
print 'Max Sequence Length: [%d]' % (maxLength)
print 'Total Sequence Length: [%d]' % (totalLength)

for fold in range(0,numberOfFolds):

	allRows = allRows.sample(frac=1)
	split = len(allRows)/2
	trainRows = allRows[:split]
	testRows = allRows[split:]

	print '\tTraining rows: [%d]' % (len(trainRows))
	print '\tTest rows: [%d]' % (len(testRows))

	for modelType in modelTypes:

		print "Running fold: [%d] model: [%s]" % (fold, modelType)

		if (modelType == "bow"):
			print '\tExtraction BOW Training Features...'
			X_train, y_train = extractBowFeatures(trainRows, totalLength, maxLength)
			print '\tExtraction BOW Test Features...'
			X_test, y_test = extractBowFeatures(testRows, totalLength, maxLength)
		elif (modelType == "avg"):
			print '\tExtraction Avg Training Features...'
			X_train, y_train = extractAvgFeatures(trainRows, totalLength, maxLength)
			print '\tExtraction Avg Test Features...'
			X_test, y_test = extractAvgFeatures(testRows, totalLength, maxLength)
		else:
			print '\tExtraction Training Features...'
			X_questions_train, X_captions_train, y_train = extractFeatures(trainRows, totalLength, maxLength)
			print '\tExtraction Test Features...'
			X_questions_test, X_captions_test, y_test = extractFeatures(testRows, totalLength, maxLength)

		# print 'Total data samples: [%d]' % (len(y_train) + len(y_test))
		# print '\tTraining data size: [%d]' % (len(y_train))
		# print '\tTest data size: [%d]' % (len(y_test))

		outputResultsFile = os.path.join(results.outputPath, "%s-%d-outputTestResults.csv" % (modelType, fold))
		outputStatsFile = os.path.join(results.outputPath, "%s-%d-outputStats.csv" % (modelType, fold))
		outputModelFile = os.path.join(results.outputPath, "%s-%d-model-weights.hd5" % (modelType, fold))

		metrics = ['accuracy', 'precision','recall','fmeasure']

# bow: 200,150,100
# all: 150,150,100

		if (modelType == "bow"):
			decoder = Sequential()
			decoder.add(Dense(300, input_dim=len(word_index), activation='relu'))
			decoder.add(Dense(200, activation='relu'))
			decoder.add(Dense(150, activation='relu'))
			decoder.add(Dense(len(word_index), activation='softmax'))
			decoder.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=metrics)

		elif (modelType == "avg"):
			decoder = Sequential()
			decoder.add(Dense(200, input_dim=wordVectorSize*2, activation='relu'))
			decoder.add(Dense(150, activation='relu'))
			decoder.add(Dense(100, activation='relu'))
			decoder.add(Dense(len(word_index), activation='softmax'))
			decoder.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=metrics)

		elif(modelType in ['capOnly','quesOnly']):
			encoder_a = Sequential()
			encoder_a.add(LSTM(200, input_shape=(maxLength,wordVectorSize)))

			decoder = Sequential()
			decoder.add(encoder_a)
			decoder.add(Dense(150, activation='relu'))
			decoder.add(Dense(100, activation='relu'))
			decoder.add(Dense(len(word_index), activation='softmax'))
			decoder.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=metrics)

		elif (modelType == "all-bidirect"):
			encoder_a = Sequential()
			encoder_a.add(Bidirectional(LSTM(200), input_shape=(maxLength,wordVectorSize)))

			encoder_b = Sequential()
			encoder_b.add(Bidirectional(LSTM(200), input_shape=(maxLength,wordVectorSize)))

			decoder = Sequential()
			decoder.add(Merge([encoder_a, encoder_b], mode='concat'))
			decoder.add(Dense(150, activation='relu'))
			decoder.add(Dense(100, activation='relu'))
			decoder.add(Dense(len(word_index), activation='softmax'))
			decoder.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=metrics)
			
		elif (modelType == "all"):
			encoder_a = Sequential()
			encoder_a.add(LSTM(200, input_shape=(maxLength,wordVectorSize)))

			encoder_b = Sequential()
			encoder_b.add(LSTM(150, input_shape=(maxLength,wordVectorSize)))

			decoder = Sequential()
			decoder.add(Merge([encoder_a, encoder_b], mode='concat'))
			decoder.add(Dense(150, activation='relu'))
			decoder.add(Dense(100, activation='relu'))
			decoder.add(Dense(len(word_index), activation='softmax'))
			decoder.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=metrics)


		# if fold == 1:
		# 	print(decoder.summary())
		# print(decoder.get_config())

		finalScores = []

		def test():
			names = ['loss','acc', 'precision', 'recall', 'fmeasure']
			if (modelType in ['all','all-bidirect']):
				scores = decoder.test_on_batch([X_questions_test, X_captions_test], y_test)
			elif(modelType == 'quesOnly'):
				scores = decoder.test_on_batch(X_questions_test, y_test)
			elif(modelType == 'capOnly'):
				scores = decoder.test_on_batch(X_captions_test, y_test)
			elif(modelType in ["bow","avg"]):
				scores = decoder.test_on_batch(X_test, y_test)
			totalScores = dict(zip(decoder.metrics_names, scores))
			global finalScores
			finalScores.append(totalScores)
			print '\nTest: ' + ' - '.join([n + ": " + str(float(totalScores[n])) for n in names])

		class TestCallback(keras.callbacks.Callback):

			def on_epoch_end(self, epoch, logs={}):
				# print ''
				test()
		testCallback = TestCallback()
		if (modelType  in ['all','all-bidirect']):
			decoder.fit([X_questions_train, X_captions_train],y_train, nb_epoch=numberOfEpochs, verbose=1, callbacks=[testCallback], batch_size=200)
		elif(modelType == 'quesOnly'):
			decoder.fit(X_questions_train,y_train, nb_epoch=numberOfEpochs, verbose=1, callbacks=[testCallback], batch_size=200)
		elif(modelType == 'capOnly'):
			decoder.fit(X_captions_train,y_train, nb_epoch=numberOfEpochs, verbose=1, callbacks=[testCallback], batch_size=200)
		elif(modelType in ["bow","avg"]):
			decoder.fit(X_train,y_train, nb_epoch=numberOfEpochs, verbose=1, callbacks=[testCallback], batch_size=200)

		test()

		if (modelType in ['all','all-bidirect']):
			y_predict = decoder.predict_proba([X_questions_test, X_captions_test], verbose=0)
		elif(modelType == 'quesOnly'):
			y_predict = decoder.predict_proba(X_questions_test, verbose=0)
		elif(modelType == 'capOnly'):
			y_predict = decoder.predict_proba(X_captions_test, verbose=0)
		elif(modelType in ["bow","avg"]):
			y_predict = decoder.predict_proba(X_test, verbose=0)
		

		y_predict_words = []
		test_captions = []
		index = 0
		for _,t in testRows.iterrows():
			best = np.argmax(y_predict[index])
			imageFilename = t['image']
			test_captions.append(imageCaptions[imageFilename])
			y_predict_words.append(index_word[best])
			index+=1

		testRows['caption'] = pd.Series(test_captions, index=testRows.index)
		testRows['predict'] = pd.Series(y_predict_words, index=testRows.index)
		testRows.to_csv(outputResultsFile)
		pd.DataFrame(finalScores).to_csv(outputStatsFile)

		decoder.save_weights(outputModelFile)
