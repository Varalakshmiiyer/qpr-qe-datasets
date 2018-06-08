import pandas as pd
import time
from collections import OrderedDict
import random

outputDirectory = "../data/visual-genome/5-26-2016/"
questionType = 'what'

questionsDf = pd.read_csv(outputDirectory + questionType + '-questions-withNouns.csv')
regionsDf = pd.read_csv(outputDirectory + questionType + '-regions-onlyNouns.csv')
regionNounsDf = pd.read_csv(outputDirectory + questionType + '-nounList.csv')

outputFile = questionType + '-alteredQuestions.csv'

tic = time.time()

invalidWords = set(['color'])

allNouns = set([w.lower() for w in regionNounsDf['word'].tolist()])

allNouns -= invalidWords

repeatTimes = 10
allData = []
for index, d in questionsDf.iterrows():
	questionRegions = regionsDf[regionsDf['coco_id']==d['coco_id']]

	imageNouns = set([n.lower() for n in questionRegions['noun'].tolist()])
	imageNouns -= invalidWords
	if not(pd.isnull(d['nouns'])) and len(d['nouns']) > 0:
		questionItems = {i.split('|')[0].lower():i.split('|')[1] for i in d['nouns'].split(';') if '|' in i}
		questionNouns = set(questionItems.keys())
		questionNouns -= invalidWords
		if (len(imageNouns) > 0 and len(questionNouns) > 0):
			# print d['question']
			# print questionNouns
			# print imageNouns
			chooseList = list((allNouns - imageNouns) - questionNouns)
			for i in range(0,repeatTimes):
				replace = random.choice(list(questionNouns))
				replaceWith = random.choice(chooseList)
				data = OrderedDict()
				data['question'] = d['question']
				data['questionId'] = d['questionId']
				data['coco_id'] = d['coco_id']
				data['questionType'] = questionType
				data['alteredQuestion'] = d['question'].replace(replace,replaceWith)
				# data.update({'questionId': d['questionId'], 'question': d['question'], 'coco_id': d['coco_id'], 'alteredQuestion':d['question'].replace(replace,replaceWith)})
				allData.append(data)
			# print len(chooseList)

print len(allNouns)
# print allNouns

pd.DataFrame(allData, columns=['question','questionId','coco_id','questionType', 'alteredQuestion']).to_csv(outputDirectory + outputFile)


print 'Done (t=%0.2fs)'%(time.time()- tic)