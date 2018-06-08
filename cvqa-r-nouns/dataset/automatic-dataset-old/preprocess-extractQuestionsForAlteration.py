import pandas as pd
import time
import os

inputDirectory = "../data/visual-genome/5-26-2016/"
questionType = 'what'

tic = time.time()

dataTypes = ['regions','questions']
for dataType in dataTypes:
	outputFile = inputDirectory  + 'filteredByCoco/' +  questionType + '-' + dataType + '-withCocoId.csv'
	df = pd.read_csv(inputDirectory + questionType + '-' + dataType + '.csv')
	cocoIds = df['coco_id'].dropna()
	df = df[df['coco_id'].isin(cocoIds)]
	df.sort_values(['coco_id']).to_csv(outputFile)
print 'Done (t=%0.2fs)'%(time.time()- tic)