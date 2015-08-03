#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import jieba,jieba.posseg,jieba.analyse


class Node:

	def __init__(self,name,children):
		self.parent = set([])
		self.name = ""  
		self.children = []

	def addChild(self,node):
		self.children.append(node)

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
		#如果它的父节点只有它自己的话，则认为它是根节点,添加到最终要输出的root_set中
		if len(category_parent_dict[parent_name]) == 1 and list(category_parent_dict[parent_name])[0][0] == parent_name:
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


def getNodeChildren(category_parent_dict):
	node_children_dict = {}
	for category in category_parent_dict.keys():
		for parent in category_parent_dict[category]:
			parent_name = parent[0]	
			node_children_dict.setdefault(parent_name,set([])).add(category)
	return node_children_dict

def getNodeChildren2(category_parent_dict):
	node_dict = {}
	for category in category_parent_dict.keys():
		node_dict[category] = {'name':category,'pnames':category_parent_dict[category],'children':[]}
	for category in node_dict.keys():
		for parent in node_dict[category]['pnames']:
			parent_name = parent[0]
			relation_weight = parent[1]
			if relation_weight != 0:
				node_dict[parent_name]['children'].append(node_dict[category])
	for category in node_dict.keys():
		del node_dict[category]['pnames']
	return node_dict

def main():
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

	category_parent_dict = createCategoryTree(synonym_dict,partial_dict,combine_dict)

	#输出json
	tree = getNodeChildren2(category_parent_dict)
	for node_name in tree.keys():
		if len(tree[node_name]['children']) == 0:
			del tree[node_name]

	print tree
	json_tree = {}
	json_tree['name'] = 'root'
	json_tree['children'] = []
	for node_name in tree.keys():
		json_tree['children'].append(tree[node_name])

	print json_tree
	encodedjson = json.dumps(json_tree)
	outfile = open('category_visualization.json','wb')
	outfile.write(encodedjson)


if __name__ == '__main__':
	main()

