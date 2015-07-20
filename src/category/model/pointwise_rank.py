#encoding=utf-8
import sys
sys.path.append('../../common/')
import file_utils
import numpy as np
from sklearn import svm
from sklearn import tree
from sklearn.externals import joblib
from sklearn import linear_model
from sklearn.kernel_ridge import KernelRidge
from sklearn.ensemble import RandomForestClassifier



data_path = '../'

def getFeature(category_id):
	category_feature_dict = {}
	infile = open('../feature/combine_feature/'+str(category_id)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		features = [float(val) for val in items[1:]]
		category_feature_dict.setdefault(category,features)
	return category_feature_dict

def readTrainData(category_feature_dict,category_path):
	print 'reading train data'
	X = []
	Y = []
	infile = open('train_data/train_pointwise_'+category_path+'.csv','rb')
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
	# clf = linear_model.LinearRegression()
	# clf = KernelRidge(alpha=1.0)
	# clf = RandomForestClassifier(n_estimators=10)
	clf = tree.DecisionTreeClassifier()
	# clf = svm.SVC()
	clf = clf.fit(X, Y)
	joblib.dump(clf, 'classifier.model',compress=3)
	return clf

def test(clf,X_test,X_test_name,category_id):
	print 'testing'
	outfile = open('result_pointwise/'+str(category_id)+'.txt','wb')
	label_category_dict = {}
	for i in range(len(X_test)):
		x_test = X_test[i]
		x_test_name = X_test_name[i]
		result = clf.predict(x_test)[0]
		label_category_dict.setdefault(result,[]).append(x_test_name)
	sorted_list = sorted(label_category_dict.items(),key=lambda p:p[0],reverse=True)
	for record in sorted_list:
		for x_test_name in record[1]:
			outfile.write(x_test_name+','+str(record[0])+'\r\n')	
	# for label in label_category_dict.keys():
	# 	for x_test_name in label_category_dict[label]:
	# 		outfile.write(x_test_name+','+str(label)+'\r\n')

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')
	file_utils.createDirs(['result_pointwise'])

	category_feature_dict = getFeature(category_path)
	X_train,Y = readTrainData(category_feature_dict,category_path)
	X_test,X_test_name = readTestData(category_feature_dict)
	clf = model(X_train,Y)
	test(clf,X_test,X_test_name,category_path)

	# category_feature_dict = getFeature(category_path)
	# X_test,X_test_name = readTestData(category_feature_dict)
	# clf = joblib.load('classifier.model')
	# test(clf,X_test,X_test_name,category_path)


if __name__ == '__main__':
	main(u'54_牌')