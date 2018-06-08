import os
import pandas as pd
import os
import json
baseFolder = "/sb-personal/cvqa/data/visual-genome/7-11-2016"

alteredQuestionsFile = os.path.join(baseFolder,"alteredQuestions.csv")
df = pd.read_csv(alteredQuestionsFile)

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(os.path.join(baseFolder, filename)) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

imageData = readJson('image_data.json')
qaToImageIndexMapping = readJson('qa-to-image-indexMapping.json')

types = ['list1', 'list2', 'list3']
for replacementType in types:
	print "%s: %d" % (replacementType, len(df[df['replacementType'] == replacementType]))

print "Images: %d" % (len(df['qa_id'].unique()))
print "Original questions: %d" % (len(df['qa_id'].unique()))

# print imageData
print 'Image Data: %d' % (len(imageData))
print 'Mapping: %d' % (len(qaToImageIndexMapping))

urls = {}
for index,i in enumerate(df['qa_id'].unique()):
	imageIndex = qaToImageIndexMapping[str(i)]
	urls[imageData[imageIndex]['url']] = True
	# print index,imageData[imageIndex]['url']

urls = urls.keys()

for i,u in enumerate(urls):
	print i,u

