#encoding=utf-8
import sys
import os
import jieba
import jieba.posseg as pseg
import jieba.analyse
import math

data_path = '../../../../data/'

def getStopword():
	stop_word_addr = data_path+'stopword.txt'
	stop_word_set = set()
	fi = open(stop_word_addr, 'rb')
	for line in fi:
		stop_word_set.add(line.strip().decode('utf-8'))
	fi.close()
	return stop_word_set

def readDir(dir_path):
	file_path_list = []
	files = os.listdir(dir_path)
	for f in files:
		file_path_list.append(dir_path+f)
	return file_path_list

def readCategoryInfo(file_path_list):
	print 'reading category info'
	category_info_dict = {}
	file_index = 0
	for file_path in file_path_list:
		file_index += 1
		print file_index
		category = file_path.split('/')[-1]
		category = unicode(category,'gbk').decode('utf-8')
		category_info_dict.setdefault(category,{})
		infile = open(file_path,'rb')
		for row in infile:
			item = row.strip().split(',')
			word = item[0].decode('utf-8')
			fre = int(item[1])
			category_info_dict[category].setdefault(word,fre)
	return category_info_dict

def extractFeature(category_id,toClearAmbiguity,main_category_keywords,relevant_category_list,sub_category_list,category_info_dict):
	print 'validating'
	stop_word_set = getStopword()
	sub_category_score_dict = {}
	for sub_category in sub_category_list:
		words_set = set(category_info_dict[sub_category].keys())
		main_category_keywords_set = set(main_category_keywords)
		intersect_num = len(words_set&main_category_keywords_set)
		if intersect_num >= 2 or not toClearAmbiguity:
			for relevant_category in relevant_category_list:
				main_to_sub_score = 0
				if sub_category in category_info_dict[relevant_category].keys():
					main_to_sub_score = category_info_dict[relevant_category][sub_category]
				sub_to_main_score = 0
				if relevant_category in category_info_dict[sub_category].keys():
					sub_to_main_score = category_info_dict[sub_category][relevant_category]
				total_score = 0
				# if main_to_sub_score != 0 and sub_to_main_score != 0:
				total_score = main_to_sub_score+sub_to_main_score
				sub_category_score_dict[sub_category] = total_score
		else:
			sub_category_score_dict[sub_category] = 0

	outfile = open('feature/category_feature_baidu_'+str(category_id)+'.csv','wb')
	
	max_score = max(sub_category_score_dict.values())
	sorted_list = sorted(sub_category_score_dict.items(),key=lambda p:p[1],reverse=True)
	for val in sorted_list:
		score_normalize = 1.0*val[1]/max_score
		outfile.write(val[0]+','+str(score_normalize)+'\r\n')
		
#判断shorter_text是否被longer_text包含
def isSubset(shorter_text,longer_text):
	is_subset = False
	for i in range(len(longer_text)):	
		if shorter_text == ''.join(longer_text[i:i+len(shorter_text)]):
			is_subset = True
		if i+len(shorter_text) == len(longer_text):
			break
	return is_subset

def getMainCategoryKeywords(relevant_category_list,category_info_dict):
	main_category_keywords = []
	for category in category_info_dict.keys():
		for relevant_category in relevant_category_list:
			if len(category) > len(relevant_category):
				if isSubset(relevant_category,category):
					print category
					main_category_keywords.append(category)
	return main_category_keywords


def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	file_path_list = readDir('../../data/category_feature/'+str(category_id)+'/clean/')
	category_info_dict = readCategoryInfo(file_path_list)
	
	toClearAmbiguity = False
	# relevant_category_list = [u'棋',u'牌']
	relevant_category_list = [u'阅读',u'新闻']
	for relevant_category in relevant_category_list:
		if len(relevant_category) <= 1:
			toClearAmbiguity = True
	main_category_keywords = getMainCategoryKeywords(relevant_category_list,category_info_dict)
	
	sub_category_list = category_info_dict.keys()
	extractFeature(category_id,toClearAmbiguity,main_category_keywords,relevant_category_list,sub_category_list,category_info_dict,)

if __name__ == '__main__':
	main(15)