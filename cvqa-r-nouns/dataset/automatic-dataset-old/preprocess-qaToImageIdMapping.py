import os
import json
baseFolder = "/sb-personal/cvqa/data/visual-genome/7-11-2016"

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(os.path.join(baseFolder, filename)) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

question_answers = readJson('question_answers.json')

mapping = {}

for i,qa in enumerate(question_answers):
	for q in qa['qas']:
		mapping[q['qa_id']] = i

jsonMapping = json.dumps(mapping, ensure_ascii=False)

with open(os.path.join(baseFolder, 'qa-to-image-indexMapping.json'), "w") as outFile:
	outFile.write(jsonMapping)