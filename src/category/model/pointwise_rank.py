#encoding=utf-8
import sys
import numpy as np
from sklearn import svm
from sklearn import tree
from sklearn.externals import joblib

data_path = '../'

def readCategory(category_id):
	print 'reading category'
	category_set = set([])
	infile = open('../../../data/candidate_category_'+str(category_id)+'.txt','rb')
	for row in infile:
		items = row.strip().split(',')
		word = items[0].decode('utf-8')
		fre = int(items[1])
		category_set.add(word)
	print '---'+str(len(category_set))
	return category_set

def combineFeature(category_id):
	# category_set = readCategory(category_id)

	category_feature_dict = {}
	print 'reading baidu feature'
	infile = open(data_path+'feature/category_feature_baidu_'+str(category_id)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		category_feature_dict.setdefault(category,[])
		category_feature_dict[category] += [score]
		category_feature_dict[category] += [len(category)]

	print 'reading wiki feature'
	infile = open(data_path+'feature/category_feature_wiki_'+str(category_id)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		feature_list = [float(val) for val in items[1:]] 
		# is_in_wiki = float(items[1])
		# average_level_in_wiki = float(items[2])
		# average_relation_level_in_wiki = float(items[3])
		# cover_num = float(items[4])
		if category in category_feature_dict.keys():
			category_feature_dict[category] += feature_list

	print 'reading title_tf feature'
	infile = open(data_path+'feature/title_tf_'+str(category_id)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category] += [score]

	print 'reading tag_tf feature'
	infile = open(data_path+'feature/tag_tf_'+str(category_id)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category] += [score]
	
	print 'reading inclusion relation feature'
	infile = open(data_path+'feature/inclusion_'+str(category_id)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category] += [score]

	print 'reading hierarchy feature'
	infile = open(data_path+'feature/hierarchy_'+str(category_id)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		feature_list = [float(val) for val in items[1:]] 
		if category in category_feature_dict.keys():
			category_feature_dict[category] += feature_list

	for category in category_feature_dict.keys():
		if len(category_feature_dict[category]) != 13:
			print category
			print len(category_feature_dict[category])
			del category_feature_dict[category]
	return category_feature_dict

def readTrainData(category_feature_dict):
	print 'reading train data'
	X = []
	Y = []
	infile = open('train_pointwise2.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		x_name = items[0].decode('utf-8')
		if x_name not in category_feature_dict.keys():
			print x_name
			continue
		x = category_feature_dict[x_name]
		label = int(items[1])
		X.append(x)
		Y.append(label)
	return X,Y

def readTestData(category_feature_dict):
	print 'reading test data'
	X_test = []
	X_test_name = []
	for category in category_feature_dict.keys():
		X_test_name.append(category)
		X_test.append(category_feature_dict[category])
	return X_test,X_test_name

def model(X,Y):
	print 'training model'
	clf = tree.DecisionTreeClassifier()
	# clf = svm.SVC()
	clf = clf.fit(X, Y)
	joblib.dump(clf, 'decision_tree_classifier.model',compress=3)
	return clf

def test(clf,X_test,X_test_name,category_id):
	print 'testing'
	outfile = open('result_pointwise_'+str(category_id)+'.txt','wb')
	label_category_dict = {}
	for i in range(len(X_test)):
		x_test = X_test[i]
		x_test_name = X_test_name[i]
		result = clf.predict(x_test)[0]
		label_category_dict.setdefault(result,[]).append(x_test_name)
	for label in label_category_dict.keys():
		for x_test_name in label_category_dict[label]:
			outfile.write(x_test_name+','+str(label)+'\r\n')

def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	# category_feature_dict = combineFeature(category_id)
	# X_train,Y = readTrainData(category_feature_dict)
	# X_test,X_test_name = readTestData(category_feature_dict)
	# clf = model(X_train,Y)
	# test(clf,X_test,X_test_name,category_id)

	category_feature_dict = combineFeature(category_id)
	X_test,X_test_name = readTestData(category_feature_dict)
	clf = joblib.load('decision_tree_classifier.model')
	test(clf,X_test,X_test_name,category_id)


if __name__ == '__main__':
	main(54)