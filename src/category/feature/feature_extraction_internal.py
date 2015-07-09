#encoding=utf-8
import sys
sys.path.append("../../common/")
import os
import text_process
import file_utils
import common
import pickle
import jieba,jieba.posseg,jieba.analyse

data_path = '../../../data/'

def inclusionRelation(category_id,category_set):
	print 'extracting inclusion relation feature'
	category_feature_dict = {}
	for category in category_set:
		category_feature_dict.setdefault(category,0)
	outfile = open('internal/'+str(category_id)+'.csv','wb')
	for i in range(len(category_feature_dict.keys())):
		for j in range(len(category_feature_dict.keys())):
			if i != j:
				word_i = category_feature_dict.keys()[i]
				word_j = category_feature_dict.keys()[j]
				if len(word_i) < len(word_j):
					if text_process.isSubset(word_i,word_j) and len(word_i)!=1:
						category_feature_dict[word_i] += 1

	inclusion_max = max(category_feature_dict.values())
	print 'sorting'
	sorted_list = sorted(category_feature_dict.items(),key=lambda p:p[1],reverse=True)
	print 'writing'
	for val in sorted_list:
		inclusion_normalize = 1.0*val[1]/inclusion_max
		outfile.write(val[0]+','+str(inclusion_normalize)+'\r\n')

def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	file_utils.createDirs(['internal'])
	category_set = common.getCandidateCategory(category_id)
	inclusionRelation(category_id,category_set)

if __name__ == '__main__':
	category_id = int(sys.argv[1])
	main(category_id)
