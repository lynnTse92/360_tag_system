#encoding=utf-8
import sys
import collections
import os

data_path = '../../../data/'

class UndirectWeightedGraph:

	def __init__(self):
		self.graph = collections.defaultdict(list)

	def addEdge(self, start, end, weight):
		# use a tuple (start, end, weight) instead of a Edge object
		self.graph[start].append((start, end, weight))
		# self.graph[end].append((end, start, weight))

def readDir(dir_path):
	file_path_list = []
	files = os.listdir(dir_path)
	for f in files:
		file_path_list.append(dir_path+f)
	return file_path_list

def readCategoryInfo(file_path_list):
	print 'reading category info'
	category_info_dict = {}
	file_index = 0
	for file_path in file_path_list:
		file_index += 1
		# print file_index
		category = file_path.split('/')[-1]
		category = category.decode('utf-8')
		# category = unicode(category,'gbk').decode('utf-8')
		category_info_dict.setdefault(category,{})
		infile = open(file_path,'rb')
		max_fre = -1
		for row in infile:
			item = row.strip().split(',')
			word = item[0].decode('utf-8')
			fre = int(item[1])
			if len(word) == 1:
				continue
			if max_fre == -1:
				max_fre = fre
			normalize_fre = 1.0*fre/max_fre
			category_info_dict[category].setdefault(word,normalize_fre)
	return category_info_dict

def generateCategoryNetwork(main_category_list,category_info_dict):
	print 'generating graph'
	g = UndirectWeightedGraph()
	for category in category_info_dict.keys():
		for relevant_word in category_info_dict[category].keys():
			w = category_info_dict[category][relevant_word]
			g.addEdge(category,relevant_word, w)
	return g

def getNeighborNodes(g,category_info_dict,query_node_list):
	neighbors_info = []
	queryed_tuple_set = set()
	for query_node in query_node_list:
		for node_info in g.graph[query_node]:
			if (node_info[0],node_info[1]) not in queryed_tuple_set and node_info[0] in category_info_dict[node_info[1]].keys():
				neighbors_info.append([node_info[0],node_info[1],node_info[2]])
				queryed_tuple_set.add((node_info[0],node_info[1]))
	return neighbors_info

def getHierarchy(g,category_info_dict,main_category_list,max_depth=3):
	print 'getting hierarchy'
	query_node_list = main_category_list
	queryed_node_list = []	
	hierarchy_node_dict = {}
	for depth in range(max_depth):
		neighbors_info = getNeighborNodes(g,category_info_dict,query_node_list)
		hierarchy_node_dict.setdefault(depth+1,neighbors_info)
		queryed_node_list += query_node_list
		neighbors = [node_info[1] for node_info in neighbors_info]
		query_node_list = list(set(neighbors) - set(queryed_node_list))
	return hierarchy_node_dict

def calculateRelation(g,hierarchy_node_dict,hierarchy_max_dict,category_hierarchy_score_dict,target_node,max_depth=3):
	for hierarchy_level in hierarchy_node_dict.keys():
		hierarchy_max_dict.setdefault(hierarchy_level,0)
		category_hierarchy_score_dict.setdefault(target_node,{}).setdefault(hierarchy_level,0)
		# print '--------------------------------'
		# print 'hierarchy_level '+str(hierarchy_level)
		level_score = 0
		counter = 0
		for node_info in hierarchy_node_dict[hierarchy_level]:
			if node_info[1] == target_node:
				reverse_score = 0
				counter += 1
				for reverse_link in g.graph[target_node]:
					if reverse_link[1] == node_info[0]:
						reverse_score = reverse_link[2]
				link_score = node_info[2]+reverse_score
				level_score += link_score
				# print node_info[0]
				# print node_info[1]
				# print node_info[2]
				# print reverse_score
				# print link_score
		final_level_score = 0
		if counter != 0:
			final_level_score = 1.0*level_score/counter
		# print final_level_score
		if final_level_score > hierarchy_max_dict[hierarchy_level]:
			hierarchy_max_dict[hierarchy_level] = final_level_score
		category_hierarchy_score_dict[target_node][hierarchy_level] = final_level_score
		# print '--------------------------------'


def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	# main_category_list = [u'阅读',u'资讯',u'新闻']
	# main_category_list = [u'棋',u'牌',u'棋牌']
	main_category_list = [u'教育',u'学习']
	
	file_path_list = readDir(data_path+'feature/category/'+str(category_id)+'/clean/')
	category_info_dict = readCategoryInfo(file_path_list)
	g = generateCategoryNetwork(main_category_list,category_info_dict)
	hierarchy_node_dict = getHierarchy(g,category_info_dict,main_category_list)


	# outfile = open('temp','wb')
	# for hierarchy_level in hierarchy_node_dict.keys():
	# 	outfile.write(str(hierarchy_level)+'\r\n')
	# 	for node in hierarchy_node_dict[hierarchy_level]:
	# 		outfile.write(str(node[1])+'\r\n')


	# for query_category in [u'书籍',u'在线',u'中心',u'基本',u'研究',u'阅读器',u'语文',u'巴菲特',u'学习',u'文化',u'投资']:
	# for query_category in [u'斗地主',u'德州',u'扑克',u'桌游',u'三张',u'象棋',u'麻将',u'三国杀',u'接龙',u'中国']:
	hierarchy_max_dict = {}
	category_hierarchy_score_dict = {}
	for query_category in category_info_dict.keys():
		print query_category
		calculateRelation(g,hierarchy_node_dict,hierarchy_max_dict,category_hierarchy_score_dict,query_category)
		# break

	outfile = open('hierarchy_'+str(category_id)+'.csv','wb')
	for category in category_hierarchy_score_dict.keys():
		outlist = []
		for level in category_hierarchy_score_dict[category].keys():
			score_nomalize = 1.0*category_hierarchy_score_dict[category][level]/hierarchy_max_dict[level]
			outlist.append(score_nomalize)
		best_level = -1
		if max(outlist) != 0:
			best_level = outlist.index(max(outlist))+1
		outfile.write(category+','+','.join([str(val) for val in outlist])+','+str(best_level)+'\r\n')


if __name__ == '__main__':
	main(102232)
