import pandas as pd
import time
import json
from pprint import pprint
import os
import urllib

inputDirectory = "../data/visual-genome/5-26-2016/"
cocoDirectory = "../data/coco/"
outputImageDirectory = cocoDirectory + "images/"
questionType = 'what'
annotationFiles = ["captions_train2014.json","captions_val2014.json"]

questionsDf = pd.read_csv(inputDirectory + questionType + '-questions-withNouns.csv')

cocoIds = list(questionsDf['coco_id'].dropna().astype(int).unique())
print cocoIds

tic = time.time()

for annotationFile in annotationFiles:
	print "Reading %s file..." % (annotationFile)
	with open(cocoDirectory + "annotations/" + annotationFile) as data_file:    
	    data = json.load(data_file)

	for image in data['images']:
		if image['id'] in cocoIds:
			cocoIds.remove(image['id'])
			url = image['coco_url']
			outputFile = outputImageDirectory + str(image['id']) + ".jpg"
			if not(os.path.exists(outputFile)):
				print "Downloading [%s]" % (url)
				urllib.urlretrieve(url, outputFile)
			print image

print cocoIds
print len(cocoIds)
print "Finished reading json file"
print 'Done (t=%0.2fs)'%(time.time()- tic)
