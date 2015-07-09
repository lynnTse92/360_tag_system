#encoding=utf-8
import sys
sys.path.append("../../common/")
import os
import text_process
import file_utils
import common
import pickle
import jieba,jieba.posseg,jieba.analyse

data_path = '../../../data/'

def title(app_name,tf_dict):
	seg_word_list = jieba.cut(app_name)
	for word in seg_word_list:
		if word in tf_dict.keys():
			tf_dict[word] += 1
	return tf_dict

def brief(seg_brief_list,tf_dict):
	for word in seg_brief_list:
		if word in tf_dict.keys():
			tf_dict[word] += 1
	return tf_dict

def tag(app_id,app_tag_dict,tf_dict):
	for tag in app_tag_dict[app_id]:
		seg_word_list = jieba.cut(tag)
		for word in seg_word_list:
			if word in tf_dict.keys():
				tf_dict[word] += 1
	return tf_dict

def tf(category_id,category_set,app_category_dict,app_tag_dict):
	print '-extracting feature'
	infile = open(data_path+'all_cn_seg_nwi_clean.txt','rb')
	stopword_set = text_process.getStopword(data_path+'stopword.txt')
	outfile_title = open('title_tf/'+str(category_id)+'.csv','wb')
	outfile_tag = open('tag_tf/'+str(category_id)+'.csv','wb')
	title_tf_dict = {}
	tag_tf_dict = {}
	for category in category_set:
		title_tf_dict.setdefault(category,0)
		tag_tf_dict.setdefault(category,0)
	row_index = 0
	for row in infile:
		row_index += 1
		items = row.strip().split("<@>")
		try:
			app_id = int(items[0])
			app_name = items[1].decode('utf-8')
			seg_brief_list = items[2].decode('utf-8').split()
		except:
			continue
		if app_category_dict[app_id][1] != category_id:
			continue

		title(app_name,title_tf_dict)
		# brief(seg_brief_list,tf_dict)
		tag(app_id,app_tag_dict,tag_tf_dict)

	max_title_tf = max(title_tf_dict.values())
	print 'sorting'
	title_sorted_list = sorted(title_tf_dict.items(),key=lambda p:p[1],reverse=True)
	for val in title_sorted_list:
		outfile_title.write(val[0]+','+str(1.0*val[1]/max_title_tf)+'\r\n')

	max_tag_tf = max(tag_tf_dict.values())
	tag_sorted_list = sorted(tag_tf_dict.items(),key=lambda p:p[1],reverse=True)
	for val in tag_sorted_list:
		outfile_tag.write(val[0]+','+str(1.0*val[1]/max_tag_tf)+'\r\n')

def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	print '-loading preparation file'
	jieba.load_userdict(data_path+"jieba_userdict.txt")
	app_tag_dict = pickle.load(open(data_path+'app_tag.dict','rb'))
	app_category_dict = pickle.load(open(data_path+'app_category.dict','rb'))

	file_utils.createDirs(['tag_tf','title_tf'])
	category_set = common.getCandidateCategory(category_id)
	tf(category_id,category_set,app_category_dict,app_tag_dict)

if __name__ == '__main__':
	category_id = int(sys.argv[1])
	main(category_id)









	