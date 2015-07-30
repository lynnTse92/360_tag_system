#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import jieba,jieba.posseg,jieba.analyse

download_times_filter = 200

#覆盖率排序
def rankTopCoverage(top_coverage_category_info_dict,category_stat_dict,all_app_counter):
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
	print u'代表标签: '+top_coverage_category
	print u'标签集合: '+' '.join(category_stat_dict[top_coverage_category][0])
	print u'当前覆盖率: '+str(category_coverage_ratio_dict[top_coverage_category])

	top_coverage_category_info_dict.setdefault(top_coverage_category,category_stat_dict[top_coverage_category][1])
	
	if len(top_coverage_category_info_dict.keys()) != 0:
		for cover_set in top_coverage_category_info_dict.values():
			already_cover_app_set = already_cover_app_set | cover_set

	print u'累计覆盖率: '+str(1.0*len(already_cover_app_set)/all_app_counter)
	return 1.0*len(already_cover_app_set)/all_app_counter

#计算覆盖率
def calculateCoverage(category_stat_dict):
	print 'loading jieba userdict'
	jieba.load_userdict('../../../data/jieba_userdict.txt')
	print 'loading stopword'
	stopword_set = text_process.getStopword('../../../data/stopword.txt')
	print 'reading app json'
	infile = open('../data/'+category_path+'.json','rb')
	all_app_counter = 0
	print u'下载次数过滤阈值: '+str(download_times_filter)
	for row in infile:
		json_obj = json.loads(row.strip())
		app_id = int(json_obj["soft_id"])
		app_name = json_obj["soft_name"]
		app_brief = json_obj["soft_brief"]
		app_download = int(json_obj["download_times"])

		if app_download < download_times_filter:
			continue

		all_app_counter += 1

		for delegate_category in category_stat_dict.keys():
			for relevant_category in category_stat_dict[delegate_category][0]:
				if relevant_category in app_name or relevant_category in app_brief:
					category_stat_dict[delegate_category][1].add(app_id)
					break

	print u'过滤之后的app总数: '+str(all_app_counter)

	top_coverage_category_info_dict = {}
	for iter_num in range(100):
		print '迭代次数: '+str(iter_num)
		coverage_ratio = rankTopCoverage(top_coverage_category_info_dict,category_stat_dict,all_app_counter)
		if coverage_ratio >= 0.9:
			break

#获取地理位置词
def getLocationCategorySet():
	print 'getting comment category'
	location_category_set = set([])
	infile = open('rule_template/location.rule','rb')
	for row in infile:
		location_category_set.add(row.strip().decode('utf-8'))
	return location_category_set

#获取情感词
def getCommenCategorySet():
	print 'getting comment category'
	comment_category_set = set([])
	infile = open('rule_template/comment.rule','rb')
	for row in infile:
		comment_category_set.add(row.strip().decode('utf-8'))
	return comment_category_set

#获取类目停用词
def getFilterCategorySet():
	print 'getting filtered category'
	filter_category_set = set([])
	infile = open('rule_template/category_filter.rule','rb')
	for row in infile:
		filter_category_set.add(row.strip().decode('utf-8'))
	return filter_category_set

#获取同义词
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

#获取偏序关系
def getCoverPair():
	print 'getting cover relationship'
	cover_dict = {}
	infile = open('rule_template/partial.rule','rb')
	for row in infile:
		row = row.strip().decode('utf-8')
		relation_weight = 1
		master = ""
		slaver = ""
		#强偏序关系
		if '>>' in row:
			relation_weight = 2
			master = row.split('>>')[0]
			slaver = row.split('>>')[1]
		#弱偏序关系
		else:
			relation_weight = 1
			master = row.split('>')[0]
			slaver = row.split('>')[1]

		cover_dict.setdefault(master,set([])).add((slaver,relation_weight))
	return cover_dict

#获取合并规则
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


def getCandidateCategory(category_path,filter_category_set,category_parent_dict):
	category_stat_dict = {}
	candidate_category_set = set([])
	
	infile = open('../feature/baidu_baike_search/'+category_path+'.csv','rb')
	for row in infile:
		category = row.strip().split(',')[0].decode('utf-8')
		if category not in filter_category_set:
			candidate_category_set.add(category)
	
	root_children_dict = getRootChildren(category_parent_dict)

	for category in candidate_category_set:
		if category not in category_parent_dict.keys():
			category_stat_dict.setdefault(category,[set([category]),set()])
		else:
			root_set = getRootSet(category_parent_dict,set([]),category_parent_dict[category])
			for root in root_set:
				category_stat_dict.setdefault(root,[root_children_dict[root],set()])
	return category_stat_dict

#同义词0，弱偏序1，强偏序2，合并3
def createCategoryTree(synonym_dict,cover_dict,combine_dict):
	category_parent_dict = {}
	for delegate in synonym_dict.keys():
		synonym_list = list(synonym_dict[delegate])
		for synonym_word in synonym_list:
			category_parent_dict.setdefault(synonym_word,set([])).add((delegate,0))

	for master in cover_dict.keys():
		if master not in category_parent_dict.keys():
			category_parent_dict.setdefault(master,set([])).add((master,0))
		for cover_tuple in cover_dict[master]:
			slaver = cover_tuple[0]
			relation_weight = cover_tuple[1]
			category_parent_dict.setdefault(slaver,set([])).add((master,relation_weight))

	for master in combine_dict.keys():
		if master not in category_parent_dict.keys():
			category_parent_dict.setdefault(master,set([])).add((master,0))
		for slaver in combine_dict[master]:
			category_parent_dict.setdefault(slaver,set([])).add((master,3))

	return category_parent_dict

def getRootSet(category_parent_dict,root_set,parent_set):
	if len(parent_set) == 0:
		return root_set
	for parent in parent_set:
		parent_name = parent[0]
		relation_weight = parent[1]
		if len(category_parent_dict[parent_name]) == 1 and list(category_parent_dict[parent_name])[0][0] == parent_name:
			root_set.add(parent_name)
			parent_set = parent_set - set([parent])
		else:
			parent_set = parent_set | category_parent_dict[parent_name]
			parent_set = parent_set - set([parent])
	return getRootSet(category_parent_dict,root_set,parent_set)

def getRootChildren(category_parent_dict):
	print '-aggregate category with same root'
	root_children_dict = {}
	for category in category_parent_dict.keys():
		root_set =  getRootSet(category_parent_dict,set([]),category_parent_dict[category])
		for root in root_set:
			root_children_dict.setdefault(root,set([])).add(category)
	return root_children_dict

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	#暂时不处理这些词
	filter_category_set = getFilterCategorySet() #类目停用词
	location_category_set = getLocationCategorySet() #地理位置词
	comment_category_set = getCommenCategorySet() #情感词
	filter_category_set = filter_category_set | comment_category_set | location_category_set

	#规则模版
	synonym_dict = getSynonym()
	cover_dict = getCoverPair()
	combine_dict = getCombine()

	#构建类目关系树
	category_parent_dict = createCategoryTree(synonym_dict,cover_dict,combine_dict)

	#候选词覆盖率统计字典
	category_stat_dict = getCandidateCategory(category_path,filter_category_set,category_parent_dict)
	calculateCoverage(category_stat_dict)

if __name__ == '__main__':
	category_path = u"17"
	main(category_path)


