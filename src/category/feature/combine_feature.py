#encoding=utf-8
import sys
sys.path.append("../../common/")
import os
import text_process
import file_utils
import common

def combineFeature(category_id,category_path,category_set):
	outfile = open('combine_feature/'+str(category_path)+'.csv','wb')
	category_feature_dict = {}
	for category in category_set:
		category_feature_dict.setdefault(category,[])
		category_feature_dict[category] += [len(category)]

	print 'reading baidu feature'
	infile = open('baidu_baike/'+str(category_path)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category] += [score]

	print 'reading wiki feature'
	infile = open('wikipedia/'+str(category_path)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		feature_list = [float(val) for val in items[1:]] 
		if category in category_feature_dict.keys():
			category_feature_dict[category] += feature_list

	print 'reading title_tf feature'
	infile = open('title_tf/'+str(category_path)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category] += [score]

	print 'reading tag_tf feature'
	infile = open('tag_tf/'+str(category_path)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category] += [score]
	
	print 'reading inclusion relation feature'
	infile = open('internal/'+str(category_id)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		score = float(items[1])
		if category in category_feature_dict.keys():
			category_feature_dict[category] += [score]

	print 'reading hierarchy feature'
	infile = open('baidu_baike_hierarchy/'+str(category_path)+'.csv','rb')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		feature_list = [float(val) for val in items[1:]] 
		if category in category_feature_dict.keys():
			category_feature_dict[category] += feature_list

	for category in category_feature_dict.keys():
		if len(category_feature_dict[category]) != 13:
			print category
			print len(category_feature_dict[category])
			del category_feature_dict[category]
	
	for category in category_feature_dict.keys():
		outfile.write(category+','+','.join([str(val) for val in category_feature_dict[category]])+'\r\n')

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	category_path_list = category_path.split('_')
	category_id = int(category_path_list[0])
	query_category = ""
	if len(category_path_list) >= 2:
		query_category = category_path_list[-1].decode('utf-8')
	main_category_list = [query_category]

	file_utils.createDirs(['combine_feature'])
	category_set = common.getCandidateCategory(category_id)
	combineFeature(category_id,category_path,category_set)

if __name__ == '__main__':
	category_path = str(sys.argv[1])
	main(category_path)