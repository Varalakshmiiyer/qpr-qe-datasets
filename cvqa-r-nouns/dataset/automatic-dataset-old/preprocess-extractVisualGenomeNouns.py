import pandas as pd
from nltk.tag.perceptron import PerceptronTagger
from nltk.tag import StanfordNERTagger
from nltk.tag.stanford import StanfordPOSTagger
import os
import nltk
import time

outputDirectory = "../data/visual-genome/5-26-2016/"
questionType = 'what'

tagger = PerceptronTagger()
tagger = StanfordPOSTagger('/sb/built/stanford-nlp/stanford-postagger-full-2015-12-09/models/wsj-0-18-bidirectional-distsim.tagger', '/sb/built/stanford-nlp/stanford-postagger-full-2015-12-09/stanford-postagger.jar')
# neTagger = StanfordNERTagger('/sb/built/stanford-nlp/stanford-ner-2015-12-09/classifiers/english.muc.7class.distsim.crf.ser.gz',
# 						'/sb/built/stanford-nlp/stanford-ner-2015-12-09/stanford-ner.jar',
# 					   	encoding='utf-8')

def get_continuous_chunks(tagged_sent):
    continuous_chunk = []
    current_chunk = []

    index = 0
    for token, tag in tagged_sent:
        if tag != "O":
            current_chunk.append((token, tag, index))
        else:
            if current_chunk: # if the current chunk is not empty
                continuous_chunk.append(current_chunk)
                current_chunk = []
    	index += 1
    # Flush the final current_chunk into the continuous_chunk, if any.
    if current_chunk:
        continuous_chunk.append(current_chunk)
    return continuous_chunk

def appendStanfordEntities(tags):
	entity_names = []
	named_entities = get_continuous_chunks(tags)
	for ne in named_entities:
		typeName = ne[0][1]
		startPosition = ne[0][2]
		endPosition = ne[-1][2]
		named_entities_str = " ".join([token for token, tag, _ in ne])
		entity_names.append({"type":typeName,"startPosition":startPosition,"endPosition":endPosition,"value":named_entities_str})
	return entity_names

def splitNouns(row):
	tagset = None
	tokens = nltk.word_tokenize(row[fieldName])
	tags = nltk.tag._pos_tag(tokens, tagset, tagger)
	# tags = neTagger.tag(tokens)
	print "\t%s" % (tags)
	# entity_names = appendStanfordEntities(tags)
	# print entity_names
	tags = [word + "|" + pos for word,pos in tags if pos.startswith('NN')]
	return ';'.join(tags)

typeNames = ['regions','questions']
fieldNames = ['phrase', 'question']

batch = True
batchSize = 250

if batch:
	for index, typeName in enumerate(typeNames):
		fieldName = fieldNames[index]
		df = pd.read_csv(outputDirectory + questionType + "-" + typeName + '.csv')
		count = len(df)
		batchDirectory = os.path.join(outputDirectory,"pos-" + typeName)
		iterationFile = os.path.join(batchDirectory,"iteration.txt")
		with open(iterationFile, "r") as iterFile:
			start = int(iterFile.read())

		batchCount = 0
		batchData = []
		for i,row in df.iterrows():
			if (i < start):
				continue

			print "Processing [%d/%d]:" % (i,count)

			data = {'i':i, 'noun':splitNouns(row)}
			batchData.append(data)
			batchCount += 1

			if (batchCount == batchSize):
				pd.DataFrame(batchData, columns=['i','noun']).to_csv(os.path.join(batchDirectory, str(i) + '.csv'))

				batchCount = 0
				batchData = []
				with open(iterationFile, "w") as iterFile:
					iterFile.write(str(i+1)) 
else:
	for index, typeName in enumerate(typeNames):
		fieldName = fieldNames[index]
		df = pd.read_csv(outputDirectory + questionType + "-" + typeName + '.csv')
		count = len(df)

		# print df

		tic = time.time()

		print 'Parsing ' + typeName + '...'
		df['nouns'] = df.apply (lambda row: splitNouns (row, count),axis=1)
	print 'Done (t=%0.2fs)'%(time.time()- tic)
	df.to_csv(outputDirectory + questionType + "-" + typeName  + '-withNouns.csv')