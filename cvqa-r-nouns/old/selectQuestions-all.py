import sys
import argparse
from gensim import *
import pandas as pd
import numpy as np
import json
import random
import os
import time
import re

def readJson(filename):
	print "Reading [%s]..." % (filename)
	with open(os.path.join(filename)) as inputFile:
		jsonData = json.load(inputFile)
	print "Finished reading [%s]." % (filename)
	return jsonData

parser= argparse.ArgumentParser(description='Train/Test CVQA Models')
parser.add_argument('-s','--sampleSize', help='Number of images to sample. Use 0 for all images',type=int)
parser.add_argument('-o','--outputDir', help='Output directory')
parser.add_argument('-b','--baseDir', help='Base input directory')

if len(sys.argv) ==1:
	parser.print_help()
	sys.exit(1)

args=parser.parse_args()

tic = time.time()

questionsFile = os.path.join(args.baseDir, 'generated-data/cvqa_questions_answers.csv')
qaToImageFile = os.path.join(args.baseDir, 'generated-data/qa-to-image-indexMapping.json')
imageDataFile = os.path.join(args.baseDir, 'source-data/image_data.json')

print "Loading Questions..."
qaToImageMapping = readJson(qaToImageFile)
questionsDf = pd.read_csv(questionsFile)
imageData = readJson(imageDataFile)

replacementTypes = questionsDf['replacementType'].unique()
print 'Replacement types: [%s]' % (repr(replacementTypes))

imageIds = questionsDf['image_id'].unique()
print 'Number of imageIds: [%d]' % (len(imageIds))

randomImageIds = [ imageIds[i] for i in sorted(random.sample(xrange(len(imageIds)), args.sampleSize)) ]

for replacementType in replacementTypes:
	allSentences = questionsDf[questionsDf['replacementType'] == replacementType]
	print 'Number of sentences for [%s]: [%d]' % (replacementType, len(allSentences))

	allSentences = allSentences[allSentences['image_id'].isin(randomImageIds)]
	print 'Number of filtered sentences for [%s]: [%d]' % (replacementType, len(allSentences))

	questionNumber = 0
	excludeWords = ['a','the','what','that','to','who','why']

	outputs={}

	for i,s in allSentences.iterrows():
		questionNumber += 1
		print "---- %d ----" % (questionNumber)
		qaId = s['qa_id']
		imageIndex = qaToImageMapping[str(qaId)]
		currentImageData = imageData[imageIndex]
		filename = currentImageData['url'].split('/')[-1]

		if (random.random() >= 0.5):
			question = s['alteredQuestion'][:-1]
			replacedWith = s['replacedWith']

			print 'Replaced with: [%s]' % (replacedWith)
			print 'Processing [%s]...' % (question)

			labelItems = []
			questionWords = []
			question = question.replace(replacedWith, '<match>')
			replacedWith = re.sub(r'[^a-zA-Z0-9_ ]','', replacedWith)
			
			for w in question.split(' '):
				w = w.strip()
				if (len(w) > 0 and w not in excludeWords):
					if w == '<match>':
						for i in replacedWith.split(' '):
							i = i.strip()
							if (i not in excludeWords):
								labelItems.append('1')
								questionWords.append(i)
					else:
						labelItems.append('0')
						questionWords.append(w)

			question = ' '.join(questionWords)
			label = ' '.join(labelItems)

			print 'Question: [%s]' % (question)
			print 'Label: [%s]' % (label)

			output = {}
			output['qa_id'] = qaId
			output['question'] = question
			output['image'] = filename
			output['label'] = label
			outputs[questionNumber] = output

		else:
			questionWords = []
			labelItems = []

			for w in s['question'][:-1].split(' '):
				w = w.strip()
				if (len(w) > 0 and w not in excludeWords):
					labelItems.append('0')
					questionWords.append(w)

			originalQuestion = ' '.join(questionWords)
			originalLabel = ' '.join(labelItems)

			print 'Original Question: [%s]' % (originalQuestion)
			print 'Original Label: [%s]' % (originalLabel)

			originalOutput = {}
			originalOutput['qa_id'] = qaId
			originalOutput['question'] = originalQuestion
			originalOutput['image'] = filename
			originalOutput['label'] = originalLabel
			outputs[questionNumber] = originalOutput
		
	outputDataFile = os.path.join(args.outputDir, 'questions-imagesPerDataset-%d-replacementType-%s.json' % (args.sampleSize, replacementType))

	with open(outputDataFile, "w") as f:
		f.write(json.dumps(outputs))


print 'Finished in (t=%0.2fs)'%(time.time()- tic)
