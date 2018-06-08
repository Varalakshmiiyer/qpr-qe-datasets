import pandas as pd
import json
import os
import sys
import re
import random
from gensim import models

reload(sys)  
sys.setdefaultencoding('utf8')

pd.options.mode.chained_assignment = None

def stat(output):
	sys.stdout.write("\r" + output)
	sys.stdout.flush()

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(filename) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

allFile = '/sb-personal/cvqa/data/cvqa/cvqa-randomQuestionDataset-filtered-all.csv'
baseFolder = '/sb-personal/cvqa/data/visual-genome/7-11-2016/'
outputFolder = '/sb-personal/cvqa/data/cvqa/'
outputFile = os.path.join(outputFolder, 'editableQuestionDataset.csv')
word2VecPath = os.path.join(outputFolder, '../word2vec/google-news/GoogleNews-vectors-negative300.bin')
subsetCount = 6000

imageData = readJson(baseFolder + 'source-data/image_data.json')
objects = readJson(baseFolder + 'source-data/objects.json')
question_answers = readJson(baseFolder + 'source-data/question_answers.json')
imageCaptions = readJson(outputFolder + 'imagecaptions.json')

print "Loading Word2Vec Dictionary. This may take a long time..."
w2v = models.Word2Vec.load_word2vec_format(word2VecPath, binary=True)

def include(word):
	return len(n.split(' ')) == 1 and (re.match("^[a-z]*$", n)) and not(n in ['the','is']) and n in w2v

urlToIndex = {}
for i, currentImageData in enumerate(imageData):
	url = os.path.basename(currentImageData['url'])
	urlToIndex[url] = i

allObjects = []
for row in objects:
	for part in row['objects']:
		 for n in part['names']:
			#Only one word objects
			# if len(n.split(' ')) == 1 and re.match("^[a-z]*$", n):
			if include(n):
				allObjects.append(n.lower())

allObjects = list(set(allObjects))

print 'All Objects: [%d]' % len(allObjects)

allRows = pd.read_csv(allFile)
allRows = allRows[allRows['image'].isin(imageCaptions)]
irrelevantQuestions = allRows[allRows['label'] == 1]
selectedImages = irrelevantQuestions['image'].unique().tolist()[:subsetCount]

total = len(selectedImages)

editableQuestions = []
for i,imageFilename in enumerate(selectedImages):
	stat('[%d/%d]' % (i+1,total))
	qId = urlToIndex[imageFilename]
	imageObjects = []
	for part in objects[qId]['objects']:
		for n in part['names']:
			#Only one word objects
			n = n.lower()
			# if len(n.split(' ')) == 1 and re.match("^[a-z]*$", n):
			if include(n):
				imageObjects.append(n)

	item = question_answers[qId]

	for q in item['qas']:
		words = re.split('[ ]+',q['question'].lower()[:-1])
		question = ' '.join(words)

		questionObjects = [w for w in words if w in imageObjects]
		if len(questionObjects) == 0:
			continue

		randomObject = random.choice(allObjects)
		while (randomObject in questionObjects):
			randomObject = random.choice(allObjects)

		randomQuestionObject = random.choice(questionObjects)

		editQuestion = ' '.join([randomObject if w==randomQuestionObject else w for w in words])

		editableQuestion = {}
		editableQuestion['qId'] = qId
		editableQuestion['image'] = imageFilename
		editableQuestion['question'] = question
		editableQuestion['editQuestion'] = editQuestion
		editableQuestion['word'] = randomQuestionObject
		editableQuestion['editedWith'] = randomObject
		editableQuestions.append(editableQuestion)

print ''
print 'Editable questions: [%d]' % (len(editableQuestions))

pd.DataFrame(editableQuestions).to_csv(outputFile)