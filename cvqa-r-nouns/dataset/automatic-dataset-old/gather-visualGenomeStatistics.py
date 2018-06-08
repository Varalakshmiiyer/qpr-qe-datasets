import pandas as pd
import time
import os

inputDirectory = "../data/visual-genome/5-26-2016/"
cocoDirectory = "../data/coco/"
outputImageDirectory = cocoDirectory + "images/"
questionType = 'what'

regionsDf = pd.read_csv(inputDirectory + questionType + '-regions-withNouns.csv')
print "Unique Regions: %d"  % (len(list(regionsDf['coco_id'].dropna())))

questionsDf = pd.read_csv(inputDirectory + questionType + '-questions-withNouns.csv')
print "Unique Questions: %d"  % (len(list(questionsDf['coco_id'].dropna())))