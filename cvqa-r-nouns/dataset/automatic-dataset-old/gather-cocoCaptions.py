import pandas as pd
import time
import json
from pprint import pprint
import os

inputDirectory = "../data/visual-genome/5-26-2016/"
cocoDirectory = "../data/coco/"
outputImageDirectory = cocoDirectory + "images/"
questionType = 'what'
annotationFiles = ["captions_train2014.json","captions_val2014.json"]

questionsDf = pd.read_csv(inputDirectory + questionType + '-questions-withNouns.csv')
outputCocoCaptionsFile = inputDirectory + questionType + '-imageCaptions-mscoco.csv'

cocoIds = list(questionsDf['coco_id'].dropna().astype(int).unique())
print cocoIds

tic = time.time()

for annotationFile in annotationFiles:
	print "Reading %s file..." % (annotationFile)
	with open(cocoDirectory + "annotations/" + annotationFile) as data_file:    
	    data = json.load(data_file)
	found = []
	for caption in data['annotations']:
		if caption['image_id'] in cocoIds:
			found.append(caption)

print cocoIds
print len(found)
print len(cocoIds)
pd.DataFrame(found).to_csv(outputCocoCaptionsFile)
print "Finished reading json file"
print 'Done (t=%0.2fs)'%(time.time()- tic)
