import pandas as pd

resultsFile = '/sb-personal/cvqa/results/randomDataset/outputTestResults-all.csv'
df = pd.read_csv(resultsFile)

countDf = df.dropna().groupby('word')
countDf = countDf.filter(lambda x: len(x) < 5)
countDf.groupby('word').count().to_csv('/sb-personal/cvqa/test.csv')

# words = df['word'].dropna().unique().tolist()

# w = 'RELEVANT'
# wordDf = df[df['label']==2]
# total = len(wordDf)
# correct = len(wordDf[wordDf['predict'] == w])

# print '%s \t[%d/%d]: \t%f%%' % (w, correct, total, float(correct)/float(total))


# print ''
# for w in words:
# 	wordDf = df[df['word']==w]
# 	wordDf = wordDf[wordDf['label']==1]

# 	total = len(wordDf)
# 	correct = len(wordDf[wordDf['predict'] == w])

# 	print '%s \t[%d/%d]: \t%f%%' % (w, correct, total, float(correct)/float(total))