import json
import os
import pandas as pd
import numpy as np

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(filename) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

baseDataDirectory = '/sb-personal/cvqa/data/'
# captionFile = os.path.join(baseDataDirectory, 'vqar/imagecaptions.json')
# imageCaptions = readJson(captionFile)

# # print imageCaptions

# # print ''
# # print ''

# newCaptions = {}
# for key in imageCaptions:
# 	newKey = os.path.basename(key)
# 	newCaptions[newKey] = imageCaptions[key]
# 	# print newKey
# 	# print key
# 	# print imageCaptions[key]
# 	# print newCaptions[newKey]

# # print newCaptions

# outputFile = os.path.join(baseDataDirectory, 'vqar/imagecaptions-new.json')
# with open(outputFile, "w") as out:
# 	out.write(json.dumps(newCaptions))

def uniquify_data(qi_applicable):
	tcount=0
	unique_qi_applicable=dict()	
	for entry in qi_applicable.items():
		if entry[1]['label']!='':
			key=entry[1]['image']+'__'+entry[1]['question']
			if key in unique_qi_applicable:
					
				unique_qi_applicable[key]['lcounts'].append(int(entry[1]['label']))
				if len(unique_qi_applicable[key]['lcounts'])>0:
					if len(unique_qi_applicable[key]['lcounts'])==2:
						tcount+=1
						#print tcount
					if np.mean(unique_qi_applicable[key]['lcounts'])>=1.5:
						unique_qi_applicable[key]['label']=2
					else:
						unique_qi_applicable[key]['label']=1
			else:
				unique_qi_applicable[key]=dict()
				unique_qi_applicable[key]['lcounts']=[]
				unique_qi_applicable[key]['lcounts'].append(int(entry[1]['label']))
				unique_qi_applicable[key]['question']=entry[1]['question']
				unique_qi_applicable[key]['image']=entry[1]['image']
				if len(unique_qi_applicable[key]['lcounts'])>0:
					if np.mean(unique_qi_applicable[key]['lcounts'])>=1.5:
						unique_qi_applicable[key]['label']=2
					else:
						unique_qi_applicable[key]['label']=1

	return unique_qi_applicable

questionFile = os.path.join(baseDataDirectory, 'vqar/RamScoresNew.json')
questions = readJson(questionFile)
questions = uniquify_data(questions)

newQuestions = []
for q in questions:
	question = questions[q]
	newQuestion = {}
	if question['label'] == 1:
		newQuestion['label'] = 2
	else:
		newQuestion['label'] = 1
	newQuestion['question'] = question['question']
	newQuestion['image'] = os.path.basename(question['image'])
	newQuestions.append(newQuestion)

df = pd.DataFrame(newQuestions)
print df.groupby('label').count()

outputFile = os.path.join(baseDataDirectory, 'vqar/vqar-comparison-dataset.csv')
df.to_csv(outputFile)