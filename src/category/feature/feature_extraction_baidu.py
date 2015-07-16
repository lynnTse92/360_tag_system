#encoding=utf-8
import sys
sys.path.append("../../common/")
import os
import text_process
import file_utils
import common
import jieba
import jieba.posseg as pseg
import jieba.analyse
import math

data_path = '../../../data/'

def readCategoryInfo(file_path_list):
	print 'reading category info'
	category_info_dict = {}
	file_index = 0
	for file_path in file_path_list:
		file_index += 1
		category = file_path.split('/')[-1]
		category = category.decode('utf-8')
		# category = unicode(category,'gbk').decode('utf-8')
		category_info_dict.setdefault(category,{})
		infile = open(file_path,'rb')
		for row in infile:
			item = row.strip().split(',')
			word = item[0].decode('utf-8')
			fre = int(item[1])
			category_info_dict[category].setdefault(word,fre)
	return category_info_dict

def extractFeature(category_id,toClearAmbiguity,main_category_keywords,main_category_list,sub_category_list,category_info_dict):
	print 'validating'
	stopword_set = text_process.getStopword(data_path+'stopword.txt')
	sub_category_score_dict = {}
	for sub_category in sub_category_list:
		words_set = set(category_info_dict[sub_category].keys())
		main_category_keywords_set = set(main_category_keywords)
		intersect_num = len(words_set&main_category_keywords_set)
		if intersect_num >= 2 or not toClearAmbiguity:
			for main_category in main_category_list:
				main_to_sub_score = 0
				if sub_category in category_info_dict[main_category].keys():
					main_to_sub_score = category_info_dict[main_category][sub_category]
				sub_to_main_score = 0
				if main_category in category_info_dict[sub_category].keys():
					sub_to_main_score = category_info_dict[sub_category][main_category]
				total_score = 0
				# if main_to_sub_score != 0 and sub_to_main_score != 0:
				total_score = main_to_sub_score+sub_to_main_score
				sub_category_score_dict[sub_category] = total_score
		else:
			sub_category_score_dict[sub_category] = 0

	outfile = open('baidu_baike/'+str(category_id)+'.csv','wb')
	
	max_score = max(sub_category_score_dict.values())
	sorted_list = sorted(sub_category_score_dict.items(),key=lambda p:p[1],reverse=True)
	for val in sorted_list:
		score_normalize = 1.0*val[1]/max_score
		outfile.write(val[0]+','+str(score_normalize)+'\r\n')

def getMainCategoryKeywords(main_category_list,category_info_dict):
	main_category_keywords = []
	for category in category_info_dict.keys():
		for relevant_category in main_category_list:
			if len(category) > len(relevant_category):
				if text_process.isSubset(relevant_category,category):
					main_category_keywords.append(category)
	return main_category_keywords

def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	file_path_list = file_utils.getFilePathList('../../scrapy/baidu_baike/crawl_data/'+str(category_id)+'/clean/')
	category_info_dict = readCategoryInfo(file_path_list)
	file_utils.createDirs(['baidu_baike'])

	toClearAmbiguity = False
	# main_category_list = [u'棋',u'牌',u'棋牌']
	# main_category_list = [u'阅读',u'新闻']
	# main_category_list = [u'教育',u'学习']
	main_category_list = [u'考试']
	# main_category_list = [u'相机']


	for relevant_category in main_category_list:
		if len(relevant_category) <= 1:
			toClearAmbiguity = True
	main_category_keywords = getMainCategoryKeywords(main_category_list,category_info_dict)
	
	sub_category_list = category_info_dict.keys()
	extractFeature(category_id,toClearAmbiguity,main_category_keywords,main_category_list,sub_category_list,category_info_dict,)

if __name__ == '__main__':
	category_id = int(sys.argv[1])
	main(category_id)

