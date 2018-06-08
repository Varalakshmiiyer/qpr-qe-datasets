import os
import json
import pandas as pd
import random

baseFolder = '/sb-personal/cvqa/data/visual-genome/7-11-2016/'
outputFolder = baseFolder + 'generated-data/'
imagesDir = baseFolder + 'images/'
questionsPerImage = 3
imagesPerDataset = 1500
outputFile = outputFolder + 'cvqa-manual-%d-questionsPerImage-%d-imagesPerDataset.csv' % (questionsPerImage,imagesPerDataset)

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(filename) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

question_answers = readJson(baseFolder + 'source-data/question_answers.json')
image_data = readJson(baseFolder + 'source-data/image_data.json')

imagesList = os.listdir(imagesDir)
# print len(imagesList)

questions = []

print 'Gathering existing questions...'

for i,qa in enumerate(question_answers):
	for q in qa['qas']:
		question = {}
		question['question'] = q['question']
		question['answer'] = q['answer']
		question['qa_id'] = q['qa_id']
		question['image_index'] = i
		question['image_filename'] = os.path.basename(image_data[i]['url'])
		questions.append(question)
	
questionsDf = pd.DataFrame(questions)
print 'Original imageIds: [%d]' % (len(questionsDf['image_index'].unique()))
questionsDf = questionsDf[questionsDf['image_filename'].isin(imagesList)]
print 'Filtered imageIds: [%d]' % (len(questionsDf['image_index'].unique()))
questions = []
newQuestions = []

imageIds = questionsDf['image_index'].unique()
imageIds = [ imageIds[i] for i in sorted(random.sample(xrange(len(imageIds)), imagesPerDataset)) ]

total = len(imageIds)

with open(outputFile, 'w') as o:
	o.write('')

header = True

for index,i in enumerate(imageIds):
	print 'Gathering new questions for image [%d/%d]' % (index+1,total)
	newQuestionsDf = questionsDf[questionsDf['image_index'] != i].sample(questionsPerImage)
	for question in newQuestionsDf.T.to_dict().values():
		question['image_index'] = i
		question['image_id'] = image_data[i]['image_id']
		question['image_url'] = image_data[i]['url']
		question['question_is_premise_true'] = ''
		question['question_error'] = ''
		question['question_error_correction'] = ''
		question['question_error_new_question'] = ''
		question['question_error_closest_match'] = ''
		question['question_error_correction_answer'] = ''
		newQuestions.append(question)

	if ((index % 100) == 0):
		with open(outputFile, 'a') as o:
			# o.write('\n')
			o.write(pd.DataFrame(newQuestions).to_csv(header=header))
		header = False
		newQuestions = []

with open(outputFile, 'a') as o:
	# o.write('\n')
	o.write(pd.DataFrame(newQuestions).to_csv(header=header))