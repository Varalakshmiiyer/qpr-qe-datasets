import os
import pandas as pd
import os
import json
import urllib
import time

baseFolder = "/sb-personal/cvqa/data/visual-genome/7-11-2016"
outputImageDirectory = baseFolder + "/images/"

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

urls = {}
for index,i in enumerate(df['qa_id'].unique()):
	imageIndex = qaToImageIndexMapping[str(i)]
	currentImageData = imageData[imageIndex]
	urls[currentImageData['image_id']] = currentImageData['url']

tic = time.time()
urlCount = len(urls)

for i,urlId in enumerate(urls):
	url = urls[urlId]
	outputFile = outputImageDirectory + str(urlId) + ".jpg"
	print 'Url[%d/%d]: %s' % (i,urlCount,url)
	if not(os.path.exists(outputFile)):
		print "\tDownloading [%s]" % (url)
		urllib.urlretrieve(url, outputFile)
	
print 'Done (t=%0.2fs)'%(time.time()- tic)
