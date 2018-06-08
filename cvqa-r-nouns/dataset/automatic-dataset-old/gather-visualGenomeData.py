from visual_genome_python_driver import api
import pandas as pd
# ids = api.GetImageIdsInRange(startIndex=2000, endIndex=2010)
# for imageId in ids:
# 	print imageId
# 	image = api.GetImageData(id=imageId)
# 	print image
# 	regions = api.GetRegionDescriptionsOfImage(id=imageId)
# 	for region in regions:
# 		print region

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

questionType = 'what'
numberOfQuestions = 2000

questions = api.GetQAofType(qtype=questionType, qtotal=numberOfQuestions)

total = len(questions)
questionData = []
regionData = []
printHeader = True
batchSize = 50

outputDirectory = "../data/visual-genome/5-26-2016/"
questionFile = outputDirectory + questionType + "-questions.csv"
regionsFile = outputDirectory + questionType + "-regions.csv"


with open(questionFile, 'w') as f:
	f.write("\n")
with open(regionsFile, 'w') as f:
	f.write("\n")

for index, question in enumerate(questions):
	data = {}
	print "Question [%d/%d]" % (index+1, total)
	data['questionId'] = question.id
	data['question'] = question.question
	data['answer'] = question.answer
	data.update(question.image.__dict__)

	# print question.id

	try:
		regions = api.GetRegionDescriptionsOfImage(id=question.image.id)
		regionTotal = len(regions)
		if (regionTotal == 0):
			print "\tSkipping question: No regions found"
			continue
		for regionIndex,region in enumerate(regions):
			# print "\tRegion: " + str(region.id)
			print "\tRegion [%d/%d]" % (regionIndex+1, regionTotal)
			regionItem = {}
			regionItem['regionId'] = region.id
			regionItem['phrase'] = region.phrase
			regionItem['regionWidth'] = region.width
			regionItem['regionHeight'] = region.height
			regionItem['x'] = region.x
			regionItem['y'] = region.y
			regionItem.update(region.image.__dict__)
			regionData.append(regionItem)
		questionData.append(data)
	except:
		print "Error getting region descriptions"
	if (len(questionData) >= batchSize):
		with open(questionFile, 'a') as f:
			f.write(pd.DataFrame(questionData).to_csv(header=printHeader))
		with open(regionsFile, 'a') as f:
			f.write(pd.DataFrame(regionData).to_csv(header=printHeader))
		printHeader = False
		questionData = []
		regionData = []

with open(questionFile, 'a') as f:
	f.write(pd.DataFrame(questionData).to_csv(header=printHeader))
with open(regionsFile, 'a') as f:
	f.write(pd.DataFrame(regionData).to_csv(header=printHeader))