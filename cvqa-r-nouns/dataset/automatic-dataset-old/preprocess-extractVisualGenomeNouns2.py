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
tagger = StanfordPOSTagger('/sb/built/stanford-nlp/stanford-postagger-full-2015-12-09/models/english-left3words-distsim.tagger', '/sb/built/stanford-nlp/stanford-postagger-full-2015-12-09/stanford-postagger.jar')

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
	print "\t%s" % (tags)
	tags = [word + "|" + pos for word,pos in tags if pos.startswith('NN')]
	return ';'.join(tags)

def splitNounData(data, separator):
	tagset = None
	tokens = nltk.word_tokenize(data)
	tags = nltk.tag._pos_tag(tokens, tagset, tagger)
	# print "\t%s" % (tags)
	tags = [word + "|" + pos for word,pos in tags if pos.startswith('NN') or word == separator]
	return ';'.join(tags)

typeNames = ['regions','questions']
fieldNames = ['phrase', 'question']

batch = True

nltk.internals.config_java(options='-mx3024m')

if batch:
	separator = '?'
	for index, typeName in enumerate(typeNames):
		fieldName = fieldNames[index]
		print "Type: [" + typeName + "]"
		df = pd.read_csv(outputDirectory + questionType + "-" + typeName + '.csv')
		cocoIds = df['coco_id'].unique()
		count = len(cocoIds)
		for i,cocoId in enumerate(cocoIds):
			print "Processing [%d/%d]:" % (i+1,count)

			currentDf = df[df['coco_id'] == cocoId]
			data = (separator + " ").join(currentDf[fieldName])
			nounData = splitNounData(data, separator)
			split = nounData.split(";" + separator + "|.")
			# print split
			splitIndex = 0 
			for j, row in currentDf.iterrows():
				if len(split) == 0:
					df.set_value(j,'nouns','')
				else:
					df.set_value(j,'nouns',split[splitIndex])
				splitIndex += 1
		df.to_csv(outputDirectory + questionType + "-" + typeName  + '-withNouns.csv')
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