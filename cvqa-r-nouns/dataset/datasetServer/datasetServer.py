from flask import Flask
from flask import request
from flask import render_template
import pandas as pd
import json
import os
import shutil

questionsPerImage = 3
imagesPerDataset = 1500
inputFile = 'static/data/cvqa-manual-%d-questionsPerImage-%d-imagesPerDataset' % (questionsPerImage,imagesPerDataset)

print 'Reading [%s]...' % (inputFile)

app = Flask(__name__)

port = int(os.getenv('VCAP_APP_PORT', 8080))

current = 0

def getInputFile(user):
	fileName = inputFile + '-' + user + '.csv'
	if not(os.path.isfile(fileName)):
		shutil.copy2(inputFile + '.csv', fileName)
	# print fileName
	return fileName

@app.route('/', methods = ['GET', 'POST'])
def index():
    return app.send_static_file('dataset.html')

@app.route('/<user>/next', methods = ['GET', 'POST'])
def next(user=None):
	userFile = getInputFile(user)
	questionsDf = pd.read_csv(userFile)
	total = len(questionsDf)
	row = questionsDf[questionsDf['question_is_premise_true'].isnull()][:1]
	row = row.fillna('')
	item = row.T.to_dict().values()[0]
	item['questionDisplay'] = item['question'][:-1]
	item['total'] = total
	item['file'] = userFile
	return json.dumps(item,indent=4), 200

@app.route('/<user>/save', methods = ['POST'])
def save(user=None):
	data = json.loads(request.data.decode())
	print data
	questionsDf = pd.read_csv(getInputFile(user))
	row = questionsDf[questionsDf['question_is_premise_true'].isnull()][:1]
	for d in data:
		questionsDf.ix[row.index,d] = data[d]
	# print row
	# print questionsDf.ix[row.index]
	# print questionsDf[questionsDf['question_is_premise_true'].isnull()][:1]
	questionsDf.to_csv(getInputFile(user))
	return json.dumps({'success':True},indent=4), 200


if __name__ == "__main__":
	# app.run(host='0.0.0.0', debug = True, use_reloader=False)
	app.run(host='0.0.0.0', port=port)