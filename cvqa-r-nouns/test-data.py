import pandas as pd
import json

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(filename) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

trainFile = '/sb-personal/cvqa/data/cvqa/cvqa-sameQuestionDataset-list5-train.csv'
testFile = '/sb-personal/cvqa/data/cvqa/cvqa-sameQuestionDataset-list5-test.csv'
captionFile = '/sb-personal/cvqa/data/cvqa/imagecaptions.json'
trainDf = pd.read_csv(trainFile)
testDf = pd.read_csv(testFile)
imageCaptions = readJson(captionFile)

def caption(s):
	return imageCaptions[s['image']]

def stat(df, objectName):
	df['caption'] = df.apply(caption, axis=1)
	filtered = df[df['word'] == objectName]
	notRelevant = filtered[filtered['label'] == 1]
	total = len(notRelevant)
	part = len(notRelevant[notRelevant['caption'].str.contains(objectName)])
	if (part > 0):
		print '\tIrrelevant with [%s]: \t[%f]' % (objectName, float(part)/total)

	relevant = filtered[filtered['label'] == 2]
	total = len(relevant)
	part = len(relevant[relevant['caption'].str.contains(objectName)])
	if (part > 0):
		print '\tRelevant with [%s]: \t[%f]' % (objectName,float(part)/total)

list1 = ['dog','cat','horse','man','woman','boy','girl','car','bus','van','motorcycle','truck','flower','tree']
for objectName in list1:
	print 'Train:'
	stat(trainDf, objectName)
	print 'Test:'
	stat(testDf, objectName)


# print testDf[testDf['image'].isin()]

# rows = readJson(trainFile)

# stats = {0:0,1:0}
# questionKeys = rows.keys()
# for i,questionRowIndex in enumerate(questionKeys):
# 	questionRow = rows[questionRowIndex]
# 	labels = [int(l) for l in questionRow['wordLabels'].split(' ')]
# 	stats[labels.count(0)]+=1

# print stats