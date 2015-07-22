#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import pickle
import jieba,jieba.posseg,jieba.analyse

def stat(top_coverage_category_info_dict,category_stat_dict,all_app_counter):
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

def calculateCoverage(category_stat_dict):
	print 'loading jieba userdict'
	jieba.load_userdict('../../../data/jieba_userdict.txt')
	print 'loading stopword'
	stopword_set = text_process.getStopword('../../../data/stopword.txt')
	print 'reading app json'
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
	
	print all_app_counter

	top_coverage_category_info_dict = {}
	for iter_num in range(100):
		stat(top_coverage_category_info_dict,category_stat_dict,all_app_counter)

def getLocationCategorySet():
	print 'getting comment category'
	location_category_set = set([])
	infile = open('rule_template/location.rule','rb')
	for row in infile:
		location_category_set.add(row.strip().decode('utf-8'))
	return location_category_set

def getCommenCategorySet():
	print 'getting comment category'
	comment_category_set = set([])
	infile = open('rule_template/comment.rule','rb')
	for row in infile:
		comment_category_set.add(row.strip().decode('utf-8'))
	return comment_category_set

def getFilterCategorySet():
	print 'getting filtered category'
	filter_category_set = set([])
	infile = open('rule_template/category_filter.rule','rb')
	for row in infile:
		filter_category_set.add(row.strip().decode('utf-8'))
	return filter_category_set

def getSynonym():
	print 'getting synonym set'
	synonym_set_list = []
	synonym_dict = {}
	infile = open('rule_template/synonym.rule','rb')
	for row in infile:
		delegate = row.strip().split('@')[0].decode('utf-8')
		synonym_set = set(row.strip().split('@')[1].decode('utf-8').split(','))
		synonym_dict.setdefault(delegate,synonym_set)
	return synonym_dict

def getCoverPair():
	print 'getting cover relationship'
	cover_dict = {}
	infile = open('rule_template/cover.rule','rb')
	for row in infile:
		main_category = row.strip().split('>>')[0].decode('utf-8')
		cover_category_set = set(row.strip().split('>>')[1].decode('utf-8').split(','))
		cover_dict.setdefault(main_category,set())
		cover_dict[main_category] = cover_dict[main_category] | cover_category_set
	return cover_dict

def getCombine():
	print 'getting combine rule'
	combine_dict = {}
	infile = open('rule_template/combine.rule','rb')
	for row in infile:
		main_category = row.strip().split('==')[0].decode('utf-8')
		if main_category.isdigit():
			continue
		sub_category_set = set(row.strip().split('==')[1].decode('utf-8').split(','))
		combine_dict.setdefault(main_category,sub_category_set)
	return combine_dict


def getSubCategory(category_path,filter_category_set,category_parent_dict):
	category_stat_dict = {}
	subcategory_set = set([])
	
	infile = open('../feature/baidu_baike_search/'+category_path+'.csv','rb')
	counter = 0
	for row in infile:
		# counter += 1
		# if counter > 500:
		# 	break
		category = row.strip().split(',')[0].decode('utf-8')
		if category not in filter_category_set:
			subcategory_set.add(category)
	
	root_children_dict = getRootChildren(category_parent_dict)

	for subcategory in subcategory_set:
		root = getRoot(category_parent_dict,subcategory)
		if root == None:
			category_stat_dict.setdefault(subcategory,[set([subcategory]),set()])
		else:
			category_stat_dict.setdefault(root,[root_children_dict[root],set()])
	return category_stat_dict

def getRoot(category_parent_dict,category):
	if category in category_parent_dict.keys():
		if category_parent_dict[category] != category:
			return getRoot(category_parent_dict,category_parent_dict[category])
		else:
			return category
	else:
		return None

def createCategoryTree(synonym_dict,cover_dict,combine_dict):
	category_parent_dict = {}

	for delegate in synonym_dict.keys():
		if delegate not in category_parent_dict.keys():
			category_parent_dict[delegate] = delegate	
		synonym_list = list(synonym_dict[delegate])
		for i in range(len(synonym_list)):
			category_parent_dict[synonym_list[i]] = delegate

	for master in cover_dict.keys():
		if master not in category_parent_dict.keys():
			category_parent_dict[master] = master
		cover_list = list(cover_dict[master])
		for i in range(len(cover_list)):
			category_parent_dict[cover_list[i]] = master

	for master in combine_dict.keys():
		if master not in category_parent_dict.keys():
			category_parent_dict[master] = master
		combine_list = list(combine_dict[master])
		for i in range(len(combine_list)):
			category_parent_dict[combine_list[i]] = master

	return category_parent_dict

def getRootChildren(category_parent_dict):
	print '-aggregate category with same root'
	root_children_dict = {}
	for category in category_parent_dict.keys():
		root = getRoot(category_parent_dict,category)
		root_children_dict.setdefault(root,set([])).add(category)
	return root_children_dict

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	location_category_set = getLocationCategorySet()
	comment_category_set = getCommenCategorySet()
	filter_category_set = getFilterCategorySet()
	filter_category_set = filter_category_set | comment_category_set | location_category_set
	synonym_dict = getSynonym()
	cover_dict = getCoverPair()
	combine_dict = getCombine()	
	category_parent_dict = createCategoryTree(synonym_dict,cover_dict,combine_dict)

	# root = root = getRoot(category_parent_dict,u'流程管理')
	# print root

	category_stat_dict = getSubCategory(category_path,filter_category_set,category_parent_dict)
	calculateCoverage(category_stat_dict)

if __name__ == '__main__':

	category_path = u"17"
	main(category_path)











