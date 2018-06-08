import json
import os
import random
import pandas as pd
import time
import sys
import re
import operator

reload(sys)  
sys.setdefaultencoding('utf8')

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(filename) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

def stat(output):
	sys.stdout.write("\r" + output)
	sys.stdout.flush()

baseFolder = '/sb-personal/cvqa/data/visual-genome/7-11-2016/'
outputFolder = '/sb-personal/cvqa/data/cvqa/'

imageData = readJson(baseFolder + 'source-data/image_data.json')
objects = readJson(baseFolder + 'source-data/objects.json')
question_answers = readJson(baseFolder + 'source-data/question_answers.json')
image_captions = readJson(outputFolder + 'imagecaptions.json')
outputNameTemplate = 'cvqa-randomQuestionDataset-filtered-%s.csv'

minObjectCount = 10
subsetCount = 5000

print 'Image data: [%d]' % (len(imageData))
print 'Objects [%d]' % (len(objects))
print 'Question Answers [%d]' % (len(question_answers))

tic = time.time()

total = len(question_answers)

objectToImage = {}
validQIds = []
allUrls = []

for qId,item in enumerate(question_answers):
	stat('[%d/%d]' % (qId+1,total))
	currentImageData = imageData[qId]
	url = os.path.basename(currentImageData['url'])
	if (url not in image_captions):
		continue

	allUrls.append(url)

	validQIds.append(qId)
	for item in objects[qId]['objects']:
		for n in item['names']:
			if n not in objectToImage:
				objectToImage[n] = {}
			objectToImage[n][url] = True

print ''

subsetIndexes = random.sample(range(0, len(question_answers)), subsetCount)

total = len(subsetIndexes)

questionToObjects = {}
allQuestions = []

print 'Selecting questions...'

for i,qId in enumerate(subsetIndexes):
	stat('[%d/%d]' % (i+1,total))

	if (qId not in validQIds):
		continue

	item = question_answers[qId]

	currentImageData = imageData[qId]
	url = os.path.basename(currentImageData['url'])

	imageObjects = []
	for part in objects[qId]['objects']:
		for n in part['names']:
			#Only one word objects
			if len(n.split(' ')) == 1:
				imageObjects.append(n)

	for q in item['qas']:
		words = re.split('[ ]+',q['question'].lower()[:-1])
		question = ' '.join(words)

		questionObjects = [w for w in words if w in imageObjects]
		if len(questionObjects) == 0:
			continue

		questionToObjects[question] = questionObjects

		# Irrelevant question
		randomQuestionObject = random.choice(questionToObjects[question])
		urlsWithObject = objectToImage[randomQuestionObject]
		urlsWithoutObject = [u for u in allUrls if u not in urlsWithObject]
		randomUrlWithoutObject = random.choice(urlsWithoutObject)

		irrelevantQuestion = {}
		irrelevantQuestion['question'] = question
		irrelevantQuestion['image'] = randomUrlWithoutObject
		irrelevantQuestion['label'] = 1
		irrelevantQuestion['wordLabels'] = ' '.join(['0' if w==randomQuestionObject else '1' for w in words])
		irrelevantQuestion['word'] = randomQuestionObject
		allQuestions.append(irrelevantQuestion)

		# Relevant question
		relevantQuestion = {}
		relevantQuestion['question'] = question
		relevantQuestion['image'] = url
		relevantQuestion['label'] = 2
		relevantQuestion['wordLabels'] = ' '.join(['1' for w in words])
		relevantQuestion['word'] = randomQuestionObject
		allQuestions.append(relevantQuestion)

print ''

selectedQuestionsDf = pd.DataFrame(allQuestions)
print 'Question Rows: [%d]' % (len(selectedQuestionsDf))

print 'Filtering rows for object counts > [%d]...' % (minObjectCount)

selectedQuestionsDf = selectedQuestionsDf.groupby('word')
selectedQuestionsDf = selectedQuestionsDf.filter(lambda x: len(x) > minObjectCount)

print 'Question Rows: [%d]' % (len(selectedQuestionsDf))

outputFilePath = os.path.join(outputFolder,outputNameTemplate % ("all"))
print 'Saving selected questions to [%s]' % (outputFilePath)
selectedQuestionsDf.to_csv(outputFilePath)

# selectedQuestionsDf = selectedQuestionsDf.sort_values(['image'])

# selectedQuestionsDf = selectedQuestionsDf.sample(frac=1)

# outputFilePath = os.path.join(outputFolder,outputNameTemplate % ("train"))
# print 'Saving selected questions to [%s]' % (outputFilePath)
# selectedQuestionsDf[:total/2].to_csv(outputFilePath)

# outputFilePath = os.path.join(outputFolder,outputNameTemplate % ("test"))
# print 'Saving selected questions to [%s]' % (outputFilePath)
# selectedQuestionsDf[total/2:].to_csv(outputFilePath)

print 'Done (t=%0.2fs)'%(time.time()- tic)
