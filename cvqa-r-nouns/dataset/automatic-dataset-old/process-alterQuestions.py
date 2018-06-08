import json
import os
import random
import pandas as pd
import time
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

baseFolder = "/sb-personal/cvqa/data/visual-genome/7-11-2016"

alteredQuestionsFile = os.path.join(baseFolder,"alteredQuestions.csv")

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(os.path.join(baseFolder, filename)) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

def selectRandom(choices, checkAgainst):
	selected = False
	attempts = 0
	maxAttempts = 10
	while not selected:
		choice = random.choice(choices)
		attempts+=1
		if (choice not in checkAgainst):
			selected = True
			break
		if attempts > maxAttempts:
			choice = ''
			break
	return choice

def loadReplaceList3():
	replaceList3Df = pd.read_csv(baseFolder + "/replaceList3.csv", names=['search','replaceString'])
	replaceList3Df['replace'] = replaceList3Df.apply (lambda row: row['replaceString'].split('|'),axis=1)

	newItems = []

	for i,item in replaceList3Df.iterrows():
		for j in item['replace']:
			newList = list(item['replace'])
			newList.remove(j)
			newList.append(item['search'])

			newItems.append({'search':j,'replaceString':"|".join(newList),'replace':newList})

	replaceList3Df = replaceList3Df.append(pd.DataFrame(newItems))
	return replaceList3Df

replaceList3Df = loadReplaceList3()
# print replaceList3Df

objectsDf = pd.read_csv(baseFolder + "/allObjects.csv")
objectsDf = objectsDf.drop(objectsDf.columns[[0]], axis=1)

# imageData = readJson('image_data.json')
objects = readJson('objects.json')
question_answers = readJson('question_answers.json')
# region_descriptions = readJson('region_descriptions.json')
# qa_to_region_mapping = readJson('qa_to_region_mapping.json')

# print 'Image data: [%d]' % (len(imageData))
print 'Objects [%d]' % (len(objects))
print 'Question Answers [%d]' % (len(question_answers))
# print 'Region descriptions [%d]' % (len(region_descriptions))

replaceList1 = ['dog', 'cat','chair', 'plane', 'table', 'building', 'window', 'shirt', 'bird', 'door']
replaceList2 =  objectsDf['object'].tolist()
replaceLists = {'list1':replaceList1,'list2':replaceList2, 'list3':replaceList3Df}

numberOfObjects = len(objects)

printHeader = True
with open(alteredQuestionsFile, "w") as f:
	f.write('')

tic = time.time()

for objectIndex,objectList in enumerate(objects):
	alteredQuestions = []
	currentObjects = []
	for item in objectList['objects']:
		currentObjects += item['names']

	currentObjects = list(set(currentObjects))
	print 'Row [%d/%d]' % (objectIndex+1,numberOfObjects)
	# print '\tCurrent objects: [%s]' % (currentObjects)

	for item in question_answers[objectIndex]['qas']:
		matched = False
		# print '\tOriginal: %s' % (item['question'])
		words = item['question'][:-1].split(' ')
		for currentObject in currentObjects:
			if (currentObject in words):
				for replaceListName in replaceLists:
					replaceList = replaceLists[replaceListName]
					if (replaceListName == 'list3'):
						if currentObject in replaceList['search'].unique():
							replaceList = replaceList[replaceList['search'] == currentObject]['replace'].tolist()[0]
						else:
							continue
					replaceItem= selectRandom(replaceList, currentObjects)
					if (replaceItem == '' or not isinstance(replaceItem, basestring)):
						continue

					# print '\t\tReplace item: ' + repr(replaceItem)
					alteredQuestion = ' '.join([w.replace(currentObject, replaceItem) for w in words]) + '?'
					alteredData = item.copy()
					alteredData['replacementType'] = replaceListName
					alteredData['toReplace'] = currentObject
					alteredData['replacedWith'] = replaceItem
					alteredData['alteredQuestion'] = alteredQuestion
					# print '\t\tAltered [%s]: %s' % (replaceListName,alteredQuestion)
					alteredQuestions.append(alteredData)
					# print alteredData
					matched = True
			# print matched
	df = pd.DataFrame(alteredQuestions)
	with open(alteredQuestionsFile, "a") as f:
		f.write(df.to_csv(header=printHeader))
	printHeader = False

print 'Done (t=%0.2fs)'%(time.time()- tic)
# for q in alteredQuestions:
# 	print q
# print imageData[0]
# print objects[0]
# print question_answers[:10]
# print region_descriptions[:10]
# for key in ['986768','986769']:
# 	print qa_to_region_mapping[key]