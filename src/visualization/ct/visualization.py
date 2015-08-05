#encoding=utf-8
import sys
import json
import jieba,jieba.posseg,jieba.analyse


#获取同义词
def getSynonym():
	print 'getting synonym set'
	synonym_dict = {}
	handled_set = set([]) #存储已经处理过的词
	infile = open('../../category/rule/rule_template/synonym.rule','rb')
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
	infile = open('../../category/rule/rule_template/partial.rule','rb')
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
	infile = open('../../category/rule/rule_template/combine.rule','rb')
	for row in infile:
		row = row.strip().decode('utf-8')
		main_category = row.split('==')[0]
		if main_category.isdigit():
			continue
		sub_category_set = set(row.split('==')[1].split(','))
		combine_dict.setdefault(main_category,sub_category_set)
	return combine_dict

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

def convertJsonTree(category_parent_dict):
	node_dict = {}
	for category in category_parent_dict.keys():
		node_dict[category] = {'name':category,'pnames':category_parent_dict[category],'children':[]}

	for category in node_dict.keys():
		for parent in node_dict[category]['pnames']:
			parent_name = parent[0]
			relation_weight = parent[1]
			if relation_weight != 0 and relation_weight != -1:
				node_dict[parent_name]['children'].append(node_dict[category])

	for category in node_dict.keys():
		for parent in node_dict[category]['pnames']:
			parent_name = parent[0]
			relation_weight = parent[1]
			if relation_weight == 0:
				node_dict[parent_name]['children'] += node_dict[category]['children']

	for category in node_dict.keys():
		if len(node_dict[category]['pnames']) == 0:
			node_dict[category].setdefault('is_connect_root',1)
		else:
			node_dict[category].setdefault('is_connect_root',0)
	for category in node_dict.keys():
		del node_dict[category]['pnames']

	return node_dict

def main():
	reload(sys)
	sys.setdefaultencoding('utf-8')

	#获取规则模版
	synonym_dict = getSynonym()
	partial_dict = getPartial()
	combine_dict = getCombine()

	category_parent_dict = createCategoryTree(synonym_dict,partial_dict,combine_dict)

	#输出json
	tree = convertJsonTree(category_parent_dict)
	for node_name in tree.keys():
		#去除不与根节点相连的和没有孩子的
		if len(tree[node_name]['children']) == 0 or tree[node_name]['is_connect_root'] != 1:
			del tree[node_name]

	json_tree = {}
	json_tree['name'] = u'类目树'
	json_tree['children'] = []
	for node_name in tree.keys():
		json_tree['children'].append(tree[node_name])

	encodedjson = json.dumps(json_tree)
	outfile = open('data.json','wb')
	outfile.write(encodedjson)


if __name__ == '__main__':
	main()

