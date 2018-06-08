import json
import os
import pandas as pd

baseFolder = "/sb-personal/cvqa/data/visual-genome/7-11-2016"

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(os.path.join(baseFolder, filename)) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

objects = readJson('objects.json')
print 'Objects [%d]' % (len(objects))

allObjects = []
for currentObjects in objects:
	for item in currentObjects['objects']:
		allObjects += [i.encode('utf-8').lower() for i in item['names']]

allObjects = list(set(allObjects))

print 'All objects: [%s]' % (len(allObjects))

pd.DataFrame(allObjects, columns=['object']).to_csv(baseFolder + "/allObjects.csv")