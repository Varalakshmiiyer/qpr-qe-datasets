import numpy as np
from gensim import *

excludeWords = ['a','the','what','that','to','who','why']
labelName = 'wordLabels'

class W2VFeatureExtractor:

	def __init__(self, args):
		print "Loading Word2Vec Dictionary. This may take a long time..."
		self.w2v = models.Word2Vec.load_word2vec_format(args.word2VecPath, binary=True)
	
	def extractSentenceFeatures(self, w2v, sentence, maxLength):
		# print 'Extracting features for [%s]' % (sentence)
		words=sentence.split(' ')
		features=np.zeros((maxLength,300))
		selected = []
		usedWords = []
		wordIndex=0
		for word in words:
			selectedValue = False
			if word in w2v:
				if not(word.lower() in excludeWords):
					features[wordIndex]=w2v[word]
					wordIndex+=1
					usedWords.append(word)
					selectedValue = True
			selected.append(selectedValue)
		return np.asarray(features), selected, usedWords

	def extractFeatures(self, questions, image_captions, args):
		w2v = self.w2v
		questionNumber = 0
		outputs = []
		question_features=[]
		caption_features=[]
		applicable_labels=[]
		totalQuestions = len(questions)
		for i,questionIndex in enumerate(questions):
			questionNumber += 1
			# print "---- [%d/%d] ----" % (questionNumber,totalQuestions)
			s = questions[questionIndex]
			if (len(s[labelName].split(' ')) > args.maxQuestionLength):
				# print 'Skipping question: [%s] Label length: [%d]' % (s['question'], len(s[labelName]))
				continue
			filename = s['image']

			# #print "Generating Question_features..."
			ques_features, selected, usedWords = self.extractSentenceFeatures(w2v, s['question'], args.maxQuestionLength)

			#print "Generating Caption_features..."
			caption = image_captions[filename]
			cap_features, _, cap_usedWords = self.extractSentenceFeatures(w2v, caption, args.maxQuestionLength)

			label=np.zeros(args.maxQuestionLength)

			outputLabelIndex = 0
			# print len(selected)
			# print selected
			# print s['question']
			# print s[labelName].split(' ')
			for labelIndex, l in enumerate(s[labelName].split(' ')):
				# print labelIndex
				if (selected[labelIndex] == True):
					label[outputLabelIndex] = int(l)
					# # Reverse the label encoding, as the input file was encoded in an opposite fashion.
					# # 0 should now be a false premise and 1 should be a true premise
					# if (int(l) == 0):
					# 	label[outputLabelIndex] = 1
					# else:
					# 	label[outputLabelIndex] = 0
					outputLabelIndex += 1
		
			label = np.asarray(label)

			for wordIndex in range(0,len(usedWords)):
				# print '\tProcessing split [%d]...' % (wordIndex)

				currentFeatures=np.zeros((args.windowSize,300))
				windowSizeSplit = (args.windowSize - 1) / 2
				qIndex = 0
				sentenceWords = []
				for n in range(wordIndex-windowSizeSplit, wordIndex+windowSizeSplit+1):
					if n >= 0 and n < len(usedWords):
						currentFeatures[qIndex] = ques_features[n]
						sentenceWords.append(usedWords[n])
					else:
						sentenceWords.append('_')
					qIndex+=1
				currentLabel = label[wordIndex]

				output = {}
				output['question'] = s['question']
				# output['qa_id'] = s['qa_id']
				output['image'] = s['image']
				output['phrase'] = ' '.join(sentenceWords)
				output['label'] = currentLabel
				output['originalLabel'] = repr(label)
				output['caption'] = caption
				output['usedCaption'] = ' '.join(cap_usedWords)

				outputs.append(output)
				currentFeatures = np.asarray(currentFeatures)
				question_features.append(currentFeatures)
				caption_features.append(cap_features)
				applicable_labels.append(currentLabel)

			# question_features.append(ques_features)
			# caption_features.append(cap_features)
			# applicable_labels.append(label)

		question_features=np.asarray(question_features)
		caption_features=np.asarray(caption_features)
		applicable_labels=np.asarray(applicable_labels)
		print 'question_features shape'
		print question_features.shape
		print 'caption_features shape'
		print caption_features.shape
		print 'label shape'
		print applicable_labels.shape


		data = {}
		data['X'] = question_features
		data['X_cap'] = caption_features
		data['y'] = applicable_labels
		data['outputs'] = outputs

		return data

class WMDistanceFeatureExtractor:
	def __init__(self, args):
		self.ex = W2VFeatureExtractor(args)

	def extractFeatures(self, questions, image_captions, args):
		data = self.ex.extractFeatures(questions, image_captions, args)

		wmd_features = []
		outputs = data['outputs']

		print 'Extracting distance features...'

		for i,o in enumerate(outputs):
			# print '\tAveraging row [%d]' % (i)
			features=np.zeros((args.windowSize))
			caption = o['usedCaption'].split(' ')
			phrase = o['phrase'].split(' ')
			index = 0
			for p in phrase:
				if (not(p == '_')):
					features[index] = self.ex.w2v.wmdistance([p],caption)
			# print ques.shape
			# print cap.shape
			wmd_features.append(features)

		wmd_features=np.asarray(wmd_features)

		print 'wmd_features shape'
		print wmd_features.shape

		newData = {}
		newData['outputs'] = data['outputs']
		newData['y'] = data['y']
		newData['X'] = wmd_features
		newData['X_cap'] = np.zeros(len(outputs))
		return newData


class AverageFeatureExtractor:

	def __init__(self, args):
		self.ex = W2VFeatureExtractor(args)

	def extractFeatures(self, questions, image_captions, args):
		data = self.ex.extractFeatures(questions, image_captions, args)

		average_features = []
		question_features = data['X']
		caption_features = data['X_cap']

		print 'Averaging features...'

		for i in range(question_features.shape[0]):
			# print '\tAveraging row [%d]' % (i)
			ques = np.mean(question_features[i], axis=0)
			cap = np.mean(caption_features[i], axis=0)

			# print ques.shape
			# print cap.shape
			average_features.append(np.concatenate((ques,cap),0))

		average_features=np.asarray(average_features)

		print 'average_features shape'
		print average_features.shape

		newData = {}
		newData['outputs'] = data['outputs']
		newData['y'] = data['y']
		newData['X'] = average_features
		newData['X_cap'] = np.zeros(question_features.shape[0])
		return newData

