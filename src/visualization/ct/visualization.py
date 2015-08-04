#encoding=utf-8
import sys
import json
import jieba,jieba.posseg,jieba.analyse


#获取同义词
def getSynonym():
	print 'getting synonym set'
	synonym_set_list = []
	synonym_dict = {}
	infile = open('../../category/rule/rule_template/synonym.rule','rb')
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
	infile = open('../../category/rule/rule_template/partial.rule','rb')
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
	infile = open('../../category/rule/rule_template/combine.rule','rb')
	for row in infile:
		main_category = row.strip().split('==')[0].decode('utf-8')
		if main_category.isdigit():
			continue
		sub_category_set = set(row.strip().split('==')[1].decode('utf-8').split(','))
		combine_dict.setdefault(main_category,sub_category_set)
	return combine_dict

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

def getNodeChildren(category_parent_dict):
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
		relation_sum = sum([val[1] for val in node_dict[category]['pnames']])
		if relation_sum == 0:
			node_dict[category].setdefault('is_root',1)
		else:
			node_dict[category].setdefault('is_root',0)
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
	tree = getNodeChildren(category_parent_dict)
	for node_name in tree.keys():
		if len(tree[node_name]['children']) == 0 or tree[node_name]['is_root'] != 1:
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

