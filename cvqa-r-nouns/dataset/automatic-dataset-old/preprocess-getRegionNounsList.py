import pandas as pd
import time
from collections import OrderedDict

outputDirectory = "../data/visual-genome/5-26-2016/"
questionType = 'what'

regionsDf = pd.read_csv(outputDirectory + questionType + '-regions-withNouns.csv')
# df = pd.read_csv('data/regions.csv')

tic = time.time()

print 'Parsing all nouns...'
allNouns = OrderedDict({})
regionNouns = []
for index, d in regionsDf.iterrows():
	n = d['nouns']
	if (pd.isnull(n)):
		continue
	for i in n.split(";"):
		if len(i) > 0:
			noun = i.split("|")
			allNouns[noun[0]] = noun[1]
			regionNouns.append({"coco_id":d['coco_id'],"noun":noun[0], "pos": noun[1]})
# print nouns
# print len(nouns)

df = pd.DataFrame(allNouns.items(), columns=['word', 'pos'])
df.to_csv(outputDirectory + questionType + '-nounList.csv')

pd.DataFrame(regionNouns, columns=['coco_id','noun', 'pos']).to_csv(outputDirectory + questionType + '-regions-onlyNouns.csv')
print 'Done (t=%0.2fs)'%(time.time()- tic)