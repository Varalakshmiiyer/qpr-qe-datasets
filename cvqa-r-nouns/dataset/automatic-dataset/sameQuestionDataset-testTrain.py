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

def filter(questionRows):
	questionStats = {}
	counter = {}

	for i,questionRow in questionRows.iterrows():
		question = questionRow['question'] 
		if question not in questionStats:
			questionStats[question] = {'question':question,'relevant':0,'irrelevant':0}
			counter['question'] = 0

		if questionRow['label'] == 1:
			questionStats[question]['irrelevant'] += 1
		elif questionRow['label'] == 2:
			questionStats[question]['relevant'] += 1

	df = pd.DataFrame(questionStats.values())
	df['min'] = pd.concat([df['irrelevant'], df['relevant']], axis=1).min(axis=1)
	print 'Irrelevant: [%d]'  % (len(df[df['irrelevant'] > 0]))
	print 'Relevant: [%d]' % (len(df[df['relevant'] > 0]))
	# print len(df[df['min'] > 40])
	subset = df[df['min'] > 10]

	questionDf = questionRows
	questionDf['selected'] = 0
	for i,s in subset.iterrows():
		minVal = s['min']
		all = questionDf[questionDf['question'] == s['question']]
		questionDf.ix[all[all['label'] == 1].sample(minVal).index, 'selected'] = 1
		questionDf.ix[all[all['label'] == 2].sample(minVal).index, 'selected'] = 1

	print 'Not Selected: [%d]' % (len(questionDf[questionDf['selected'] == 0]))
	print 'Selected [%d]' % (len(questionDf[questionDf['selected'] == 1]))

	return questionDf[questionDf['selected'] == 1]

baseFolder = '/sb-personal/cvqa/data/visual-genome/7-11-2016'
outputFolder = '/sb-personal/cvqa/data/cvqa/'

imageData = readJson(baseFolder + '/source-data/image_data.json')
objects = readJson(baseFolder + '/source-data/objects.json')
question_answers = readJson(baseFolder + '/source-data/question_answers.json')
image_captions = readJson('/sb-personal/questionCaptionMatchModels/base-cvqa/data/imagecaptions.json')
outputNameTemplate = 'cvqa-sameQuestionDataset-sameObjectsMostCommonQuestionsOnlyIrrelevant-%s.csv'

# list1 = ['dog','cat','horse','man','woman']
# list1 = ['boy','girl','car','bus','van','motorcycle','truck','flower','tree']
list1 = ['dog','cat','horse','man','woman','boy','girl','car','bus','van','motorcycle','truck','flower','tree']
questionSubsetCount = 10
subsetCount = 2
# splitTypes = {'train':['dog','cat','horse','man','woman'], 'test':['boy','girl','car','bus','van','motorcycle','truck','flower','tree']}
splitTypes = {'train':list1, 'test':list1}

print 'Image data: [%d]' % (len(imageData))
print 'Objects [%d]' % (len(objects))
print 'Question Answers [%d]' % (len(question_answers))

tic = time.time()

usedImages = []
top = True

for splitType in splitTypes:
	# top = not(top)

	objectList = splitTypes[splitType]

	questionTemplates = {}
	for l in objectList:
		questionTemplates[l] = {}

	questionToQuestionIndexes = {}

	print 'Gathering questions...'

	total = len(question_answers)

	for i,item in enumerate(question_answers):
		stat('[%d/%d]' % (i+1,total))
		for q in item['qas']:
			words = re.split('[ ]+',q['question'].lower()[:-1])
			question = ' '.join(words)
			if (question not in questionToQuestionIndexes):
				questionToQuestionIndexes[question] = []

			questionToQuestionIndexes[question].append(i)
			for l in objectList:
				if l in words:
					if question not in questionTemplates[l].keys():
						questionTemplates[l][question] = 1
					else:
						questionTemplates[l][question] += 1

	print ''

	print 'Selecting questions...'

	selectedTemplates = {}
	for l in questionTemplates:
		selectedTemplates[l] = []
		print 'Type: [%s]\tItems: [%d]' % (l,len(questionTemplates[l]))
		sortedTemplates = sorted(questionTemplates[l].items(), key=operator.itemgetter(1), reverse=True)
		if (top):
			subset = sortedTemplates[:questionSubsetCount]
		else:
			subset = sortedTemplates[questionSubsetCount:(questionSubsetCount*5)]
		for (k,v) in subset:
			selectedTemplates[l].append(k)

	questionCount = 0
	imageToObjects = {}
	imageToQuestionObjects = {}
	selectedQuestions = []

	print 'Selecting relevant questions...'

	for l in questionTemplates:
		print 'Type: [%s]\tItems: [%d]' % (l,len(questionTemplates[l]))
		sortedTemplates = sorted(questionTemplates[l].items(), key=operator.itemgetter(1), reverse=True)
		if (top):
			subset = sortedTemplates[:questionSubsetCount]
		else:
			subset = sortedTemplates[questionSubsetCount:(questionSubsetCount*5)]
		for (k,v) in subset:
			print '\t[%d] Question:[%s]' % (v,k)
			questionCount += len(questionToQuestionIndexes[k])
			for qId in questionToQuestionIndexes[k]:
				currentImageData = imageData[qId]
				url = os.path.basename(currentImageData['url'])
				if (url not in image_captions):
					# print '\t\tSkipping missing image caption [%s]' % (url)
					continue
				if (url in usedImages):
					continue
				if url not in imageToObjects:
					imageToObjects[url] = {item:False for item in list1}
					imageToQuestionObjects[url] = {item:False for item in list1}
					for item in objects[qId]['objects']:
						for n in item['names']:
							if n in list1:
								imageToObjects[url][n] = True
				if not imageToQuestionObjects[url][l]:
					selectedQuestion = {}
					selectedQuestion['question'] = k
					selectedQuestion['image'] = url
					selectedQuestion['label'] = 2
					selectedQuestion['wordLabels'] = ' '.join(['1' for w in k.split()])
					selectedQuestion['word'] = l
					selectedQuestions.append(selectedQuestion)
					imageToQuestionObjects[url][l] = True

	print 'All Questions: [%d]' % (questionCount)
	print 'Selected Questions: [%d]' % (len(selectedQuestions))
	print 'Images: [%d]' % (len(imageToObjects))

	print 'Selecting irrelevant questions...'
	for url in imageToQuestionObjects:
		flags = imageToQuestionObjects[url]
		possibleObjects = [o for o in flags if (not(flags[o]) and not(flags[o]))]
		subset = [possibleObjects[i] for i in sorted(random.sample(xrange(len(possibleObjects)), subsetCount)) ]
		for o in subset:
			if len(selectedTemplates[o]) > 0:
				question = random.choice(selectedTemplates[o])
				selectedQuestion = {}
				selectedQuestion['question'] = question
				selectedQuestion['image'] = url
				selectedQuestion['label'] = 1
				selectedQuestion['wordLabels'] = ' '.join(['0' if w==o else '1' for w in question.split()])
				selectedQuestion['word'] = o
				selectedQuestions.append(selectedQuestion)

	print 'Irrelevant Selected Questions: [%d]' % (len(selectedQuestions))

	selectedQuestionsDf = pd.DataFrame(selectedQuestions)
	selectedQuestionsDf = filter(selectedQuestionsDf)

	print 'Filtered Questions: [%d]' % (len(selectedQuestionsDf))

	usedImages += selectedQuestionsDf['image'].tolist()

	outputFilePath = os.path.join(outputFolder,outputNameTemplate % (splitType))
	print 'Saving selected questions to [%s]' % (outputFilePath)

	selectedQuestionsDf.to_csv(outputFilePath)

print 'Done (t=%0.2fs)'%(time.time()- tic)
