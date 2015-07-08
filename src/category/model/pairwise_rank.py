#encoding=utf-8
import sys
import numpy as np
from sklearn import svm
from sklearn.externals import joblib

def combineFeature():
	category_feature_dict = {}
	print 'reading baidu feature'
	infile = open('feature/category_feature_baidu_15.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		category_feature_dict.setdefault(category,[0,0,0,0,0,0,0,0,0])
		category_feature_dict[category][0] = score
		category_feature_dict[category][7] = len(category)

	print 'reading wiki feature'
	infile = open('feature/category_feature_wiki_15.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		is_in_wiki = float(items[1])
		average_level_in_wiki = float(items[2])
		average_relation_level_in_wiki = float(items[3])
		cover_num = float(items[4])
		if category in category_feature_dict.keys():
			category_feature_dict[category][1] = is_in_wiki
			category_feature_dict[category][2] = average_level_in_wiki
			category_feature_dict[category][3] = average_relation_level_in_wiki
			category_feature_dict[category][4] = cover_num

	print 'reading title_tf feature'
	infile = open('feature/title_tf_15.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category][5] = score

	print 'reading tag_tf feature'
	infile = open('feature/tag_tf_15.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category][6] = score
	
	print 'reading inclusion relation feature'
	infile = open('feature/inclusion_15.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category][8] = score

	return category_feature_dict

def readTrainData():
	print 'reading train data'
	pairs = []
	infile = open('feature/train_pairwise.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		pairs.append([val.decode('utf-8') for val in items])
	return pairs

def getTrainFeature(pairs,category_feature_dict):
	print 'reading train feature'
	X = []
	Y = []
	for pair in pairs:
		X.append(np.array(category_feature_dict[pair[0]])-np.array(category_feature_dict[pair[1]]))
		Y.append(1)
		X.append(np.array(category_feature_dict[pair[1]])-np.array(category_feature_dict[pair[0]]))
		Y.append(0)
	return X,Y

def readTestData(category_feature_dict):
	print 'reading test data'
	pairs = []
	for i in range(len(category_feature_dict.keys())):
		for j in range(len(category_feature_dict.keys())):
			if i > j:
				pairs.append([category_feature_dict.keys()[i],category_feature_dict.keys()[j]])
		# if i >= 3000:
		# 	break
	return pairs

def getTestFeature(pairs,category_feature_dict):
	print 'reading test feature'
	X = []
	for pair in pairs:
		# print '---'
		# print pair[0]
		# print pair[1]
		# print len(category_feature_dict[pair[0]])
		# print len(category_feature_dict[pair[1]])
		# print '---'
		X.append(np.array(category_feature_dict[pair[0]])-np.array(category_feature_dict[pair[1]]))
	return X

def model(X,Y):
	print 'training model'
	clf = svm.SVC()
	clf.fit(X, Y)
	joblib.dump(clf, 'svm.model',compress=3)
	return clf

def test(clf,X_test,pairs_test):
	print 'testing'
	# outfile = open('result.txt','wb')
	results = []
	for i in range(len(X_test)):
		x_test = X_test[i]
		pair = pairs_test[i]
		result = clf.predict(x_test)[0]
		if result == 1:
			# outfile.write(pair[0]+','+pair[1]+'\r\n')
			results.append(1)
		else:
			# outfile.write(pair[1]+','+pair[0]+'\r\n')
			results.append(0)
	return results


def final(pairs_test,results):
	outfile = open('result_pairwise.rank','wb')
	category_cover_dict = {}
	for i in range(len(pairs_test)):
		pair = pairs_test[i]
		result = results[i]
		if result == 1:
			category_cover_dict.setdefault(pair[0],0)
			category_cover_dict[pair[0]] += 1
		else:
			category_cover_dict.setdefault(pair[1],0)
			category_cover_dict[pair[1]] += 1
	sorted_list = sorted(category_cover_dict.items(),key=lambda p:p[1],reverse=True)
	for val in sorted_list:
		outfile.write(val[0]+'\r\n')	


def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	category_feature_dict = combineFeature()
	pairs_train = readTrainData()
	pairs_test = readTestData(category_feature_dict)
	X_train,Y = getTrainFeature(pairs_train,category_feature_dict)
	X_test = getTestFeature(pairs_test,category_feature_dict)
	clf = model(X_train,Y)
	del category_feature_dict
	results = test(clf,X_test,pairs_test)
	final(pairs_test,results)

if __name__ == '__main__':
	main(15)