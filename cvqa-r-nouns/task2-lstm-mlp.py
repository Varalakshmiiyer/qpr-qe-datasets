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

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(filename) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

def extractFeatures(questionRows, totalLength, maxLength):

	print 'Total Question Rows: [%d]' % (len(questionRows))

	X_captions = []
	x_questions = []
	y = []

	print 'Max Sequence Length: [%d]' % (maxLength)
	print 'Total Sequence Length: [%d]' % (totalLength)

	for i,questionRow in questionRows.iterrows():
		imageFilename = questionRow['image']
		caption = imageCaptions[imageFilename]

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

		labels = newLabels
		questionWords = newQuestionWords
		captionWords = newCaptionWords

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
parser.add_argument('-tr', action='store', dest='trainFile', help='Training data file')
parser.add_argument('-te', action='store', dest='testFile', help='Test data file')
parser.add_argument('-ex', action='store', dest='experimentType', help='Experiment Type (all,quesOnly,capOnly)')
parser.add_argument('-o', action='store', dest='outputPath', help='Output path')
parser.add_argument('-e', action='store', dest='numberOfEpochs', help='Epochs', type=int)

results = parser.parse_args()

word2VecPath = '/sb-personal/cvqa/data/word2vec/google-news/GoogleNews-vectors-negative300.bin'
captionFile = '/sb-personal/cvqa/data/cvqa/imagecaptions.json'
# trainFile = '/sb-personal/cvqa/data/cvqa/cvqa-sameQuestionDataset-list5-train.csv'
# testFile = '/sb-personal/cvqa/data/cvqa/cvqa-sameQuestionDataset-list5-test.csv'

trainFile = results.trainFile
testFile = results.testFile
experimentType = results.experimentType
numberOfEpochs = results.numberOfEpochs

outputResultsFile = os.path.join(results.outputPath, "outputTestResults-%s.csv" % (experimentType))
outputStatsFile = os.path.join(results.outputPath, "outputStats-%s.csv" % (experimentType))

maxQuestionLength = 8
maxCaptionLength = 16
wordVectorSize = 300
embeddingSize = 250
# numberOfEpochs = 30
subsetCount = 4000
maxLength = 20
totalLength = maxLength * 2
# totalLength = maxLength
n_hidden = 40
excludeWordList = ['is','a','the','what','that','to','who','why']
# experimentType = 'all'

print "Loading Word2Vec Dictionary. This may take a long time..."
w2v = models.Word2Vec.load_word2vec_format(word2VecPath, binary=True)

print "Loading Captions generated by a Pre-Trained Captioning Model for Images..."
imageCaptions = readJson(captionFile)

print "Loading Questions..."

trainRows = pd.read_csv(trainFile)
testRows = pd.read_csv(testFile)

print '\tTraining rows: [%d]' % (len(trainRows))
print '\tTest rows: [%d]' % (len(testRows))

print "Removing Questions Without Matching Captions..."

trainRows = trainRows[trainRows['image'].isin(imageCaptions)]
testRows = testRows[testRows['image'].isin(imageCaptions)]

print '\tTraining rows: [%d]' % (len(trainRows))
print '\tTest rows: [%d]' % (len(testRows))

print "Extracting Vocab..."

word_index, index_word = extractVocab([trainRows, testRows])

print 'Vocab size: [%d]' % (len(word_index))

print 'Extraction Training Features...'
X_questions_train, X_captions_train, y_train = extractFeatures(trainRows, totalLength, maxLength)
print 'Extraction Test Features...'
X_questions_test, X_captions_test, y_test = extractFeatures(testRows, totalLength, maxLength)

print 'Total data samples: [%d]' % (len(y_train) + len(y_test))
print '\tTraining data size: [%d]' % (len(y_train))
print '\tTest data size: [%d]' % (len(y_test))

encoder_a = Sequential()
encoder_a.add(LSTM(40, input_shape=(maxLength,wordVectorSize)))

encoder_b = Sequential()
encoder_b.add(LSTM(40, input_shape=(maxLength,wordVectorSize)))

decoder = Sequential()
if (experimentType == 'all'):
	decoder.add(Merge([encoder_a, encoder_b], mode='concat'))
else:
	decoder.add(encoder_a)
decoder.add(Dense(40, activation='relu'))
decoder.add(Dense(15, activation='relu'))
decoder.add(Dense(len(word_index), activation='softmax'))
decoder.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy', 'precision','recall','fmeasure'])

print(decoder.summary())
print(decoder.get_config())

finalScores = []

def test():
	names = ['loss','acc', 'precision', 'recall', 'fmeasure']
	if (experimentType == 'all'):
		scores = decoder.test_on_batch([X_questions_test, X_captions_test], y_test)
	elif(experimentType == 'quesOnly'):
		scores = decoder.test_on_batch(X_questions_test, y_test)
	elif(experimentType == 'capOnly'):
		scores = decoder.test_on_batch(X_captions_test, y_test)
	totalScores = dict(zip(decoder.metrics_names, scores))
	global finalScores
	finalScores.append(totalScores)
	print '\nTest: ' + ' - '.join([n + ": " + str(float(totalScores[n])) for n in names])

class TestCallback(keras.callbacks.Callback):

	def on_epoch_end(self, epoch, logs={}):
		# print ''
		test()
testCallback = TestCallback()
if (experimentType == 'all'):
	decoder.fit([X_questions_train, X_captions_train],y_train, nb_epoch=numberOfEpochs, verbose=1, callbacks=[testCallback])
elif(experimentType == 'quesOnly'):
	decoder.fit(X_questions_train,y_train, nb_epoch=numberOfEpochs, verbose=1, callbacks=[testCallback])
elif(experimentType == 'capOnly'):
	decoder.fit(X_captions_train,y_train, nb_epoch=numberOfEpochs, verbose=1, callbacks=[testCallback])

test()

if (experimentType == 'all'):
	y_predict = decoder.predict_proba([X_questions_test, X_captions_test], verbose=0)
elif(experimentType == 'quesOnly'):
	y_predict = decoder.predict_proba(X_questions_test, verbose=0)
elif(experimentType == 'capOnly'):
	y_predict = decoder.predict_proba(X_captions_test, verbose=0)

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