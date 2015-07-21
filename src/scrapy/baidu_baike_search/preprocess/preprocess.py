#encoding=utf-8
import sys
sys.path.append("../../../common/")
import os
import text_process
import file_utils
import json
import jieba
import jieba.posseg as pseg
import jieba.analyse

data_path = '../../../../data/'

def getCandidateCategory(category_path):
	print '-reading category'
	category_set = set([])
	infile = open('../../../category/preprocess/candidate_category/'+str(category_path)+'.txt','rb')
	for row in infile:
		items = row.strip().split(',')
		word = items[0].decode('utf-8')
		fre = int(items[1])
		category_set.add(word)
	print '-category size: '+str(len(category_set))
	return category_set

def readJson(category_path):
	category_crawl_dict = {}
	infile = open('../crawl_data/'+str(category_path)+'.json','rb')
	for row in infile:
		json_str = row.strip()
		json_str = json_str.lstrip('[')
		json_str = json_str.rstrip(',')
		json_str = json_str.rstrip(']')
		# print json_str
		json_obj = json.loads(json_str)
		query_category = json_obj['query_category']
		category_crawl_dict.setdefault(query_category,[]).append(json_obj)
	return category_crawl_dict

def statRawText(score,category,text,word_score_dict,category_set,stop_word_set):
	seg_list = jieba.cut(text)
	for item in seg_list:
		if item in category_set and item not in stop_word_set:
			word_score_dict.setdefault(item,0)
			word_score_dict[item] += score

def statTextList(score,category,text_list,word_score_dict,category_set,stop_word_set):
	for item in text_list:
		if item in category_set and item not in stop_word_set:
			word_score_dict.setdefault(item,0)
			word_score_dict[item] += score

def clean(category_path,category_crawl_dict,category_set):
	print 'cleaning'
	stop_word_set = text_process.getStopword(data_path+'stopword.txt')
	for category in category_crawl_dict.keys():
		word_score_dict = {}
		outfile = open('../clean_data/'+str(category_path)+'_'+category,'wb')
		print category
		for page in category_crawl_dict[category]:
			offset_weight = 1.0*(5-int(page['offset']))/5
			
			title = page['title']
			content = page['content']
			abstract = page['abstract']

			# content_seg_list = jieba.cut(content)
			# abstract_seg_list = jieba.cut(abstract)
			# all_seg_set = set(content_seg_list) | set(abstract_seg_list)
			# intersec_num = 1.0*len(all_seg_set & category_set)/len(category_set)
			# print '------------'
			# print title
			# print 'abstract: '+abstract
			# print 'content: '+content
			# print ' '.join(all_seg_set & category_set)
			# print intersec_num
			# print '------------'
			# offset_weight = offset_weight*intersec_num
			# if intersec_num <= 0.01:
			# 	continue

			statRawText(10*offset_weight,category,title,word_score_dict,category_set,stop_word_set)
			
			statRawText(6*offset_weight,category,abstract,word_score_dict,category_set,stop_word_set)
			abstract_link = page['abstract_link']
			statTextList(10*offset_weight,category,abstract_link,word_score_dict,category_set,stop_word_set)
			abstract_bold = page['abstract_bold']
			statTextList(8*offset_weight,category,abstract_bold,word_score_dict,category_set,stop_word_set)
			
			if 'tags' in page.keys():
				tags = page['tags']
				statTextList(10*offset_weight,category,tags,word_score_dict,category_set,stop_word_set)
			
			statRawText(1*offset_weight,category,content,word_score_dict,category_set,stop_word_set)
			content_link = page['content_link']
			statTextList(4*offset_weight,category,content_link,word_score_dict,category_set,stop_word_set)
			content_bold = page['content_bold']
			statTextList(2*offset_weight,category,content_bold,word_score_dict,category_set,stop_word_set)

		sorted_list = sorted(word_score_dict.items(),key=lambda p:p[1],reverse=True)
		for val in sorted_list:
			outfile.write(val[0]+','+str(val[1])+'\r\n')

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	jieba.load_userdict("../../../../data/jieba_userdict.txt")

	file_utils.createDirs(['../clean_data'])
	category_set = getCandidateCategory(category_path)
	category_crawl_dict =readJson(category_path)
	clean(category_path,category_crawl_dict,category_set)

if __name__ == '__main__':

	category_path = u"17_笔记备忘"
	main(category_path)


