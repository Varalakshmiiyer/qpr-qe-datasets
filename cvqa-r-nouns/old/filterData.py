import pandas as pd
import json

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(filename) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

questionsFile = '/sb-personal/cvqa/data/cvqa/cvqa-sameQuestionDataset-subset-list1.json'
outputFile = '/sb-personal/cvqa/data/cvqa/cvqa-sameQuestionDataset-subset-list2.json'
questionRows = readJson(questionsFile)

output = filter(questionRows)

with open(outputFile,'w') as out:
	json.dump(output, out)