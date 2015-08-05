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
		if coverage_ratio >= 0.99:
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
	synonym_dict = {}
	handled_set = set([]) #存储已经处理过的词
	infile = open('rule_template/synonym.rule','rb')
	for row in infile:
		#该同义词集合的代表词
		delegate = row.strip().split('@')[0].decode('utf-8')
		#同义词集合
		#暂时不考虑一个词可以存在多个不同语义的同义词集合
		synonym_set = set(row.strip().split('@')[1].decode('utf-8').split(',')) - handled_set
		handled_set = handled_set | synonym_set
		synonym_dict.setdefault(delegate,synonym_set)
	return synonym_dict

#获取偏序关系
def getPartial():
	print 'getting partial relationship'
	partial_dict = {}
	infile = open('rule_template/partial.rule','rb')
	for row in infile:
		row = row.strip().decode('utf-8')
		if row == "":
			continue
		#强偏序关系2
		if '>>' in row:
			relation_weight = 2
			master = row.split('>>')[0]
			slaver = row.split('>>')[1]
		#弱偏序关系1
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
		row = row.strip().decode('utf-8')
		main_category = row.split('==')[0]
		if main_category.isdigit():
			continue
		sub_category_set = set(row.split('==')[1].split(','))
		combine_dict.setdefault(main_category,sub_category_set)
	return combine_dict

#获取类目候选词
def getCandidateCategory(category_path,filter_category_set,category_parent_dict):
	#该字典结构key->候选类目,value->数组
	#数组第一个元素是以这个候选类目为根节点的子树上所有节点构成的集合，数组第二个元素类目集合覆盖的appid集合
	category_stat_dict = {}
	candidate_category_set = set([])
	
	infile = open('../preprocess/candidate_category/'+category_path+'.txt','rb')
	for row in infile:
		category = row.strip().split(',')[0].decode('utf-8')
		if category not in filter_category_set:
			candidate_category_set.add(category)
	
	root_children_dict = getRootChildren(category_parent_dict)

	for category in candidate_category_set:
		#该候选类目不在规则库中，即与其他类目没有关系，自己是一颗树
		if category not in category_parent_dict.keys():
			category_stat_dict.setdefault(category,[set([category]),set()])
		else:
			#找出该候选类目的根节点集合
			root_set = getRootSet(category_parent_dict,set([]),category_parent_dict[category])
			for root in root_set:
				#不直接统计该候选类目的覆盖率，而是由该候选类目的根结点作为代表进行统计覆盖率
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
	

#虚节点-1,同义词0，弱偏序1，强偏序2，合并3
#维护与父节点的关系
def createCategoryTree(synonym_dict,partial_dict,combine_dict):
	category_parent_dict = {}

	#同义词
	for delegate in synonym_dict.keys():
		synonym_list = list(synonym_dict[delegate])
		for synonym_word in synonym_list:
			#如果该词是同义词集合代表词，父类为空
			if delegate == synonym_word:
				category_parent_dict.setdefault(delegate,set([]))
			else:
				category_parent_dict.setdefault(synonym_word,set([])).add((delegate,0))
	#偏序词
	for master in partial_dict.keys():
		category_parent_dict.setdefault(master,set([]))
		#虚节点，用()进行标识
		if u'(' in master and u')' in master:
			category_parent_dict.setdefault(master,set([])).add((master,-1))
		for cover_tuple in partial_dict[master]:
			slaver = cover_tuple[0]
			relation_weight = cover_tuple[1]
			if slaver in category_parent_dict.keys():
				#获取其同义词
				synonym_delegate_list = [val[0] for val in category_parent_dict[slaver] if val[1] == 0]
				if len(synonym_delegate_list) == 1:
					#如果该词有同义词代表词，父类则cover该词的同义词代表词
					category_parent_dict.setdefault(synonym_delegate_list[0],set([])).add((master,relation_weight))
				elif len(synonym_delegate_list) == 0:
					#如果该词没有同义词代表词，父类则直接cover该词
					category_parent_dict.setdefault(slaver,set([])).add((master,relation_weight))
				else:
					#该词有多个同义词代表词（异常）
					print 'multiple synonym delegates exception'
					print slaver
			else:
				category_parent_dict.setdefault(slaver,set([])).add((master,relation_weight))
	#合并词
	for master in combine_dict.keys():
		category_parent_dict.setdefault(master,set([]))
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
		#父类为空，则认为它是根节点,添加到最终要输出的root_set中
		if len(category_parent_dict[parent_name]) == 0:
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

	#候选类目词的关系树
	category_stat_dict = getCandidateCategory(category_path,filter_category_set,category_parent_dict)
	
	#通过计算覆盖率来扩充规则库
	calculateCoverage(category_parent_dict,category_stat_dict)

if __name__ == '__main__':
	category_path = u"102231"
	main(category_path)


