#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import pickle
import jieba,jieba.posseg,jieba.analyse

data_path = '../../../data/'

def stat(query_stat_dict,all_app_counter):
	coverage_app_set = set()
	intersec_app_set = set()
	counter = 0
	for main_category in query_stat_dict.keys():
		print main_category
		counter += 1
		if counter == 1:
			intersec_app_set = query_stat_dict[main_category][1]
		coverage_app_set = coverage_app_set | query_stat_dict[main_category][1]
		intersec_app_set = intersec_app_set & intersec_app_set
		query_app_counter = len(query_stat_dict[main_category][1])
		print 1.0*query_app_counter/all_app_counter

	print '-----------'
	print len(coverage_app_set)
	print len(intersec_app_set)
	print all_app_counter
	print 1.0*len(coverage_app_set)/all_app_counter

def calculateCoverage(category_path,query_stat_dict):
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

		if app_download <= 10:
			continue

		all_app_counter += 1

		seg_title_list = jieba.cut(app_name)
		seg_brief_list = jieba.cut(app_brief)

		for seg_title in seg_title_list:
			if text_process.isChinese(seg_title) and seg_title not in stopword_set:
				for main_category in query_stat_dict.keys():
					if seg_title in query_stat_dict[main_category][0]:
						query_stat_dict[main_category][1].add(app_id)

		for seg_brief in seg_brief_list:
			if text_process.isChinese(seg_brief) and seg_brief not in stopword_set: 
				for main_category in query_stat_dict.keys():
					if seg_brief in query_stat_dict[main_category][0]:
						query_stat_dict[main_category][1].add(app_id)

	stat(query_stat_dict,all_app_counter)

def getQueryCategory():
	query_stat_dict = {}
	infile = open('../data/category_hierarchy.txt','rb')
	for row in infile:
		main_category = row.strip().split('>>')[0].decode('utf-8')
		relevant_category_set = set([val.decode('utf-8') for val in row.strip().split('>>')[1].split(',')])
		query_stat_dict.setdefault(main_category,[relevant_category_set,set()])
	# query_category_set = set([u'编辑',u'笔记',u'备忘',u'任务',u'流程',u'提醒',u'工作',u'管理',u'通讯录',u'效率',u'生日'])

	return query_stat_dict

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	query_stat_dict = getQueryCategory()
	calculateCoverage(category_path,query_stat_dict)

if __name__ == '__main__':
	category_path = u"17_笔记备忘"
	main(category_path)

