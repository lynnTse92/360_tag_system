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

		if app_download < 100:
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
	for iter_num in range(20):
		stat(top_coverage_category_info_dict,category_stat_dict,all_app_counter,synonyms_set_list)

def getSynonymsSet():
	synonyms_set_list = []
	infile = open('../data/synonyms.txt','rb')
	for row in infile:
		synonyms_set_list.append(set([val.decode('utf-8') for val in row.strip().split(',')]))
	return synonyms_set_list

def getEquation():
	equation_dict = {}
	infile = open('../data/equation.txt','rb')
	for row in infile:
		main_category = row.strip().split('==')[0].decode('utf-8')
		if main_category.isdigit():
			continue
		sub_category_set = set(row.strip().split('==')[1].decode('utf-8').split(','))
		equation_dict.setdefault(main_category,sub_category_set)
	return equation_dict

def getFilterCategorySet():
	filter_category_set = set([])
	infile = open('../data/category_filter.txt','rb')
	for row in infile:
		filter_category_set.add(row.strip().decode('utf-8'))
	return filter_category_set

def getPairwise():
	pairwise_dict = {}
	infile = open('../data/pairwise.txt','rb')
	for row in infile:
		main_category = row.strip().split('>>')[0].decode('utf-8')
		sub_category_set = set(row.strip().split('>>')[1].decode('utf-8').split(','))
		pairwise_dict.setdefault(main_category,sub_category_set)
	return pairwise_dict

def getSubCategory(category_path,filter_category_set,synonyms_set_list,pairwise_dict):
	category_stat_dict = {}
	infile = open('../feature/baidu_baike_search/'+category_path+'.csv','rb')
	counter = 0
	for row in infile:
		counter += 1
		if counter > 500:
			break
		category = row.strip().split(',')[0].decode('utf-8')
		relevant_category_set = set([category])

		for synonyms_set in synonyms_set_list:
			if category in synonyms_set:
				relevant_category_set = relevant_category_set | synonyms_set
		for relevant_category in relevant_category_set:
			if relevant_category in pairwise_dict.keys():
				relevant_category_set = relevant_category_set | pairwise_dict[relevant_category]
		if category not in category_stat_dict.keys() and category not in filter_category_set:
			category_stat_dict.setdefault(category,[relevant_category_set,set()])
	return category_stat_dict

def combine(equation_dict,category_stat_dict):
	for category in category_stat_dict.keys():
		relevant_category_set = category_stat_dict[category][0]
		for exampler_category in equation_dict.keys():
			if len(relevant_category_set & equation_dict[exampler_category]) >= 1:
				if exampler_category in category_stat_dict.keys():
					category_stat_dict[exampler_category][0] = category_stat_dict[exampler_category][0] | relevant_category_set | equation_dict[exampler_category]
				else:
					category_stat_dict.setdefault(exampler_category,[relevant_category_set | equation_dict[exampler_category],set()])
	return category_stat_dict

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	filter_category_set = getFilterCategorySet()
	synonyms_set_list = getSynonymsSet()
	equation_dict = getEquation()	
	pairwise_dict = getPairwise()

	category_stat_dict = getSubCategory(category_path,filter_category_set,synonyms_set_list,pairwise_dict)
	category_stat_dict = combine(equation_dict,category_stat_dict)
	calculateCoverage(category_stat_dict,synonyms_set_list)

if __name__ == '__main__':

	category_path = u"17"
	main(category_path)











