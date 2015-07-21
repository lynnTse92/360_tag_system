#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import pickle
import jieba,jieba.posseg,jieba.analyse

data_path = '../../../data/'

def stat(top_coverage_category_info_dict,category_stat_dict,all_app_counter,synonyms_set_list):
	category_coverage_ratio_dict = {}
	already_cover_app_set = set()
	if len(top_coverage_category_info_dict.keys()) != 0:
		for cover_set in top_coverage_category_info_dict.values():
			already_cover_app_set = already_cover_app_set | cover_set

	
	for category in category_stat_dict.keys():
		cover_app_counter = len(category_stat_dict[category][1])
		intersect_with_already_cover_app_num = len(category_stat_dict[category][1] & already_cover_app_set)
		coverage_ratio = 1.0*(cover_app_counter-intersect_with_already_cover_app_num)/all_app_counter
		category_coverage_ratio_dict.setdefault(category,coverage_ratio)
	
	sorted_list = sorted(category_coverage_ratio_dict.items(),key=lambda p:p[1],reverse=True)
	

	top_coverage_category = sorted_list[0][0]
	# print top_coverage_category
	print ' '.join(category_stat_dict[top_coverage_category][0])
	print category_coverage_ratio_dict[top_coverage_category]

	top_coverage_category_info_dict.setdefault(top_coverage_category,category_stat_dict[top_coverage_category][1])
	
	if len(top_coverage_category_info_dict.keys()) != 0:
		for cover_set in top_coverage_category_info_dict.values():
			already_cover_app_set = already_cover_app_set | cover_set

	print 1.0*len(already_cover_app_set)/all_app_counter

def calculateCoverage(category_stat_dict,synonyms_set_list):
	print 'loading file'
	jieba.load_userdict(data_path+"jieba_userdict.txt")
	stopword_set = text_process.getStopword('../../../data/stopword.txt')

	print 'reading file'
	infile = open('../data/'+category_path+'.json','rb')
	all_app_counter = 0
	for row in infile:
		json_obj = json.loads(row.strip())
		app_id = int(json_obj["soft_id"])
		app_name = json_obj["soft_name"]
		app_brief = json_obj["soft_brief"]
		app_download = int(json_obj["download_times"])

		if app_download <= 10:
			continue

		all_app_counter += 1

		seg_title_list = jieba.cut(app_name)
		seg_brief_list = jieba.cut(app_brief)

		for seg_title in seg_title_list:
			if text_process.isChinese(seg_title) and seg_title not in stopword_set:
				for main_category in category_stat_dict.keys():
					if seg_title in category_stat_dict[main_category][0]:
						category_stat_dict[main_category][1].add(app_id)

		for seg_brief in seg_brief_list:
			if text_process.isChinese(seg_brief) and seg_brief not in stopword_set: 
				for main_category in category_stat_dict.keys():
					if seg_brief in category_stat_dict[main_category][0]:
						category_stat_dict[main_category][1].add(app_id)
	
	top_coverage_category_info_dict = {}
	for iter_num in range(15):
		stat(top_coverage_category_info_dict,category_stat_dict,all_app_counter,synonyms_set_list)

def getSynonymsSet():
	synonyms_set_list = []
	infile = open('../data/synonyms.txt','rb')
	for row in infile:
		synonyms_set_list.append(set([val.decode('utf-8') for val in row.strip().split(',')]))
	return synonyms_set_list

def getRelevantCategory(category_path,synonyms_set_list):
	category_stat_dict = {}
	infile = open('../feature/baidu_baike_search/'+category_path+'.csv','rb')
	counter = 0
	for row in infile:
		counter += 1
		if counter > 300:
			break
		category = row.strip().split(',')[0].decode('utf-8')
		category_synonyms_set = set([category])
		for synonyms_set in synonyms_set_list:
			if category in synonyms_set:
				category_synonyms_set = synonyms_set
		if category not in category_stat_dict.keys():
			category_stat_dict.setdefault(category,[category_synonyms_set,set()])
	return category_stat_dict

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')
	synonyms_set_list = getSynonymsSet()

	category_stat_dict = getRelevantCategory(category_path,synonyms_set_list)
	calculateCoverage(category_stat_dict,synonyms_set_list)

if __name__ == '__main__':

	category_path = u"17_笔记备忘"
	main(category_path)











