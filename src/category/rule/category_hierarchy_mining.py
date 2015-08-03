#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import jieba,jieba.posseg,jieba.analyse

download_times_filter = 200

#覆盖率排序
def rankTopCoverage(top_coverage_category_info_dict,category_stat_dict,all_app_counter):
	#子树的覆盖率
	category_coverage_ratio_dict = {}
	#已经覆盖的app
	already_cover_app_set = set()
	if len(top_coverage_category_info_dict.keys()) != 0:
		for cover_set in top_coverage_category_info_dict.values():
			already_cover_app_set = already_cover_app_set | cover_set
	
	for category in category_stat_dict.keys():
		cover_app_counter = len(category_stat_dict[category][1])
		intersect_with_already_cover_app_num = len(category_stat_dict[category][1] & already_cover_app_set)
		coverage_ratio = 1.0*(cover_app_counter-intersect_with_already_cover_app_num)/all_app_counter
		category_coverage_ratio_dict.setdefault(category,coverage_ratio)
	
	#根据每棵子树的覆盖率排序
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
def calculateCoverage(category_parent_dict,category_stat_dict):
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

		# if u'设备' in app_brief:
		# 	print app_brief

		for delegate_category in category_stat_dict.keys():
			for relevant_category in category_stat_dict[delegate_category][0]:
				if relevant_category in app_name or relevant_category in app_brief:
					if relevant_category != delegate_category:
						#如果是强联通的，根节点不需要出现
						if isStrongConnect(1,delegate_category,relevant_category,category_parent_dict):
							category_stat_dict[delegate_category][1].add(app_id)
							break
						elif delegate_category in app_name or delegate_category in app_brief:
							category_stat_dict[delegate_category][1].add(app_id)
							break
					else:
						category_stat_dict[delegate_category][1].add(app_id)
						break


	print u'过滤之后的app总数: '+str(all_app_counter)

	top_coverage_category_info_dict = {}
	for iter_num in range(100):
		print '循环次数: '+str(iter_num)
		coverage_ratio = rankTopCoverage(top_coverage_category_info_dict,category_stat_dict,all_app_counter)
		#达到一定累积覆盖率则停止
		if coverage_ratio >= 0.98:
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
		#该同义词集合的代表词
		delegate = row.strip().split('@')[0].decode('utf-8')
		#同义词集合
		synonym_set = set(row.strip().split('@')[1].decode('utf-8').split(','))
		synonym_dict.setdefault(delegate,synonym_set)
	return synonym_dict

#获取偏序关系
def getPartial():
	print 'getting cover relationship'
	partial_dict = {}
	infile = open('rule_template/partial.rule','rb')
	for row in infile:
		row = row.strip().decode('utf-8')
		#偏序关系强弱（1是弱关系，2是强关系）
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
		partial_dict.setdefault(master,set([])).add((slaver,relation_weight))
	return partial_dict

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


#获取类目候选词
def getCandidateCategory(category_path,filter_category_set,category_parent_dict):
	category_stat_dict = {}
	candidate_category_set = set([])
	
	infile = open('../preprocess/candidate_category/'+category_path+'.txt','rb')
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

#该路径是否是强联通的，前提是两个节点必须是联通的
def isStrongConnect(is_strong,target_parent,query_child,category_parent_dict):
	for parent_tuple in category_parent_dict[query_child]:
		parent_name = parent_tuple[0]
		relation = parent_tuple[1]
		#除了弱偏序关系，其他都是强关系
		if relation != 1:
			relation = 1
		else:
			relation = 0
		if parent_name != query_child:
			if parent_name == target_parent:
				return is_strong*relation
			else:
				return isStrongConnect(is_strong*relation,target_parent,parent_name,category_parent_dict)
	

#同义词0，弱偏序1，强偏序2，合并3
#维护与父节点的关系
def createCategoryTree(synonym_dict,partial_dict,combine_dict):
	category_parent_dict = {}

	for delegate in synonym_dict.keys():
		synonym_list = list(synonym_dict[delegate])
		for synonym_word in synonym_list:
			category_parent_dict.setdefault(synonym_word,set([])).add((delegate,0))

	for master in partial_dict.keys():
		if master not in category_parent_dict.keys():
			category_parent_dict.setdefault(master,set([])).add((master,0))
		for cover_tuple in partial_dict[master]:
			slaver = cover_tuple[0]
			relation_weight = cover_tuple[1]
			category_parent_dict.setdefault(slaver,set([])).add((master,relation_weight))

	for master in combine_dict.keys():
		if master not in category_parent_dict.keys():
			category_parent_dict.setdefault(master,set([])).add((master,0))
		for slaver in combine_dict[master]:
			category_parent_dict.setdefault(slaver,set([])).add((master,3))

	return category_parent_dict

#获取根节点，一个category节点可以属于多个root节点的category
def getRootSet(category_parent_dict,root_set,parent_set):
	if len(parent_set) == 0:
		return root_set
	for parent in parent_set:
		parent_name = parent[0]
		relation_weight = parent[1]
		#与其他节点只有0的关系，则认为它是根节点,添加到最终要输出的root_set中
		relation_sum = sum([val[1] for val in category_parent_dict[parent_name]])
		if relation_sum == 0:
			root_set.add(parent_name)
		#如果它不是根节点，则把它所有的父节点加入到待处理的parent_set中，直到parent_set为空才结束
		else:
			parent_set = parent_set | category_parent_dict[parent_name]
		#从parent_set中去掉已经处理过的节点
		parent_set = parent_set - set([parent])
	return getRootSet(category_parent_dict,root_set,parent_set)

#获取每一个根节点下面的所有孩子
def getRootChildren(category_parent_dict):
	print '-aggregate category with same root'
	root_children_dict = {}
	#遍历每一个category，找到它自己root，然后将category加入到root_children_dict中
	for category in category_parent_dict.keys():
		root_set =  getRootSet(category_parent_dict,set([]),category_parent_dict[category])
		for root in root_set:
			root_children_dict.setdefault(root,set([])).add(category)
	return root_children_dict

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	#暂时不处理的词放在filter_category_set中
	filter_category_set = getFilterCategorySet() #类目停用词
	location_category_set = getLocationCategorySet() #地理位置词
	comment_category_set = getCommenCategorySet() #情感词
	filter_category_set = filter_category_set | comment_category_set | location_category_set

	#获取规则模版
	synonym_dict = getSynonym()
	partial_dict = getPartial()
	combine_dict = getCombine()

	#从规则库中构建类目关系树
	category_parent_dict = createCategoryTree(synonym_dict,partial_dict,combine_dict)

	# print isStrongConnect(1,u'外语',u'背单词',category_parent_dict)

	#候选类目词的关系树
	category_stat_dict = getCandidateCategory(category_path,filter_category_set,category_parent_dict)
	
	#通过计算覆盖率来添加规则
	calculateCoverage(category_parent_dict,category_stat_dict)

if __name__ == '__main__':
	category_path = u"102231"
	main(category_path)


