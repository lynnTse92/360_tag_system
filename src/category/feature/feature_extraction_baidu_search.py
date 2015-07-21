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

def readCategoryInfo(file_path_list):
	print 'reading category info'
	category_info_dict = {}
	file_index = 0
	for file_path in file_path_list:
		file_index += 1
		category = file_path.split('/')[-1]
		category = category.decode('utf-8').split('_')[-1]
		category_info_dict.setdefault(category,{})
		infile = open(file_path,'rb')
		for row in infile:
			item = row.strip().split(',')
			word = item[0].decode('utf-8')
			fre = float(item[1])
			category_info_dict[category].setdefault(word,fre)
	return category_info_dict

def extractFeature(category_id,category_path,main_category_list,category_info_dict):
	print 'validating'
	sub_category_score_dict = {}
	sub_category_list = category_info_dict.keys()
	for sub_category in sub_category_list:
		for main_category in main_category_list:
			main_to_sub_score = 0
			if sub_category in category_info_dict[main_category].keys():
				main_to_sub_score = category_info_dict[main_category][sub_category]
			sub_to_main_score = 0
			if main_category in category_info_dict[sub_category].keys():
				sub_to_main_score = category_info_dict[sub_category][main_category]
			total_score = 0
			total_score = sub_to_main_score
			sub_category_score_dict.setdefault(sub_category,0)
			sub_category_score_dict[sub_category] += total_score

	outfile = open('baidu_baike_search/'+str(category_path)+'.csv','wb')
	
	max_score = max(sub_category_score_dict.values())
	sorted_list = sorted(sub_category_score_dict.items(),key=lambda p:p[1],reverse=True)
	for val in sorted_list[:800]:
		score_normalize = 1.0*val[1]/max_score
		outfile.write(val[0]+','+str(score_normalize)+'\r\n')

def getMainCategoryRevelantWord(query_category):
	category_relevant_set = set()
	infile = open('../data/category_hierarchy.txt','rb')
	for row in infile:
		if query_category == row.strip().decode('utf-8').split('>>')[0]:
			for relevant_word in row.strip().decode('utf-8').split('>>')[1].split(','):
				category_relevant_set.add(relevant_word)
	return category_relevant_set


def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	category_path_list = category_path.split('_')
	category_id = int(category_path_list[0])
	query_category = ""
	if len(category_path_list) >= 2:
		query_category = category_path_list[-1].decode('utf-8')
	category_relevant_set = getMainCategoryRevelantWord(query_category)
	main_category_list = list(category_relevant_set)

	file_path_list = file_utils.getFilePathList('../../scrapy/baidu_baike_search/clean_data/')
	category_info_dict = readCategoryInfo(file_path_list)
	file_utils.createDirs(['baidu_baike_search'])

	extractFeature(category_id,category_path,main_category_list,category_info_dict)

if __name__ == '__main__':
	category_path = u'17_笔记备忘'
	main(category_path)

