#encoding=utf-8
import sys
sys.path.append("../../common/")
import os
import text_process
import file_utils
import common
import json
import jieba
import jieba.posseg as pseg
import jieba.analyse

data_path = '../../../data/'

def readJosn(category_id):
	category_crawl_dict = {}
	infile = open('../../scrapy/wikipedia_search/clean_data/wikipedia_'+str(category_id)+'.json','rb')
	for row in infile:
		json_obj = json.loads(row.strip())
		query_category = json_obj['query_category']
		category_crawl_dict.setdefault(query_category,[]).append(json_obj)
	return category_crawl_dict

def stat(score,category,text,word_fre_dict,category_set,stop_word_set):
	seg_list = jieba.cut(text)
	for item in seg_list:
		if item in category_set and item not in stop_word_set:
			word_fre_dict.setdefault(item,0)
			word_fre_dict[item] += score

def stat2(score,category,text_list,word_fre_dict,category_set,stop_word_set):
	for item in text_list:
		if item in category_set and item not in stop_word_set:
			word_fre_dict.setdefault(item,0)
			word_fre_dict[item] += score

def clean(category_id,category_crawl_dict,category_set):
	print 'cleaning'
	stop_word_set = text_process.getStopword(data_path+'stopword.txt')
	for category in category_crawl_dict.keys():
		word_fre_dict = {}
		outfile = open('wiki_search/'+str(category_id)+'_'+category+'.txt','wb')
		print category
		for page in category_crawl_dict[category]:
			abstract = page['abstract']
			stat(6,category,abstract,word_fre_dict,category_set,stop_word_set)
			abstract_link = page['abstract_link']
			stat2(10,category,abstract_link,word_fre_dict,category_set,stop_word_set)
			abstract_bold = page['abstract_bold']
			stat2(8,category,abstract_bold,word_fre_dict,category_set,stop_word_set)
			if 'wiki_category' in page.keys():
				wiki_category = page['wiki_category']
				stat2(20,category,wiki_category,word_fre_dict,category_set,stop_word_set)
			if 'content' in page.keys():
				content = page['content']
				stat(1,category,content,word_fre_dict,category_set,stop_word_set)
				content_link = page['content_link']
				stat2(4,category,content_link,word_fre_dict,category_set,stop_word_set)
				content_bold = page['content_bold']
				stat2(2,category,content_bold,word_fre_dict,category_set,stop_word_set)

		sorted_list = sorted(word_fre_dict.items(),key=lambda p:p[1],reverse=True)
		for val in sorted_list:
			outfile.write(val[0]+','+str(val[1])+'\r\n')




def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	jieba.load_userdict("../../../data/jieba_userdict.txt")

	file_utils.createDirs(['wiki_search'])
	category_set = common.getCandidateCategory(category_id)
	category_crawl_dict =readJosn(category_id)
	clean(category_id,category_crawl_dict,category_set)

if __name__ == '__main__':
	main(54)