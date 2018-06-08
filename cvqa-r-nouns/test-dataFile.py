import pandas as pd

allFile = '/sb-personal/cvqa/data/cvqa/cvqa-randomQuestionDataset-filtered-all.csv'
outputFile = '/sb-personal/cvqa/analysis/datasetObjects.csv'

pd.options.mode.chained_assignment = None

allRows = pd.read_csv(allFile)

print 'Total questions: [%d]' % (len(allRows))

print 'Relevant questions: [%d]' % (len(allRows[allRows['label'] == 2]))
print 'Irrelevant questions: [%d]' % (len(allRows[allRows['label'] == 1]))

irrelevant = allRows[allRows['label'] == 1]

print 'Number of objects: [%d]' % (len(irrelevant.groupby('word')))

print irrelevant.groupby('word')['word'].count()

irrelevant.groupby('word')['word'].count().to_csv(outputFile)