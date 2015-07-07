#encoding=utf-8
import sys
import pickle
import jieba,jieba.posseg,jieba.analyse


data_path = '../../../../data/'

def isChinese(var):
	for v in var:
		if not(0x4e00<=ord(v)<0x9fa6):
			return False
	return True

def getStopword():
	infile = data_path+'stopword.txt'
	stopword_set = set()
	infile = open(infile, 'rb')
	for line in infile:
		stopword_set.add(line.strip().decode('utf-8'))
	infile.close()
	return stopword_set

def readCategory(category_id):
	print 'reading category'
	category_set = set([])
	infile = open(data_path+'candidate_concept_title_'+str(category_id)+'.txt','rb')
	for row in infile:
		items = row.strip().split(',')
		word = items[0].decode('utf-8')
		fre = int(items[1])
		category_set.add(word)
	print '---'+str(len(category_set))
	return category_set

def title(app_name,tf_dict):
	stopword_set = getStopword()
	seg_word_list = jieba.cut(app_name)
	for word in seg_word_list:
		if word in tf_dict.keys():
			tf_dict[word] += 1
	return tf_dict

def brief(seg_brief_list,tf_dict):
	stopword_set = getStopword()
	for word in seg_brief_list:
		if word in tf_dict.keys():
			tf_dict[word] += 1
	return tf_dict

def tag(app_id,app_tag_dict,tf_dict):
	stopword_set = getStopword()
	for word in app_tag_dict[app_id]:
		if word in tf_dict.keys():
			tf_dict[word] += 1
	return tf_dict

def tf(category_id,category_set,app_category_dict,app_tag_dict):
	infile = open(data_path+'all_cn_seg_nwi_clean.txt','rb')
	outfile = open('title_tf_'+str(category_id)+'.csv','wb')
	tf_dict = {}
	for category in category_set:
		tf_dict.setdefault(category,0)
	row_index = 0
	for row in infile:
		row_index += 1
		print row_index
		items = row.strip().split("<@>")
		try:
			app_id = int(items[0])
			app_name = items[1].decode('utf-8')
			seg_brief_list = items[2].decode('utf-8').split()
		except:
			continue
		if app_category_dict[app_id][1] != category_id:
			continue

		title(app_name,tf_dict)
		# brief(seg_brief_list,tf_dict)
		# tag(app_id,app_tag_dict,tf_dict)

	max_tf = max(tf_dict.values())
	print 'sorting'
	sorted_list = sorted(tf_dict.items(),key=lambda p:p[1],reverse=True)
	for val in sorted_list:
		outfile.write(val[0]+','+str(1.0*val[1]/max_tf)+'\r\n')

def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	print 'loading preparation file'
	jieba.load_userdict(data_path+"jieba_userdict.txt")
	app_tag_dict = pickle.load(open(data_path+'app_tag.dict','rb'))
	app_category_dict = pickle.load(open(data_path+'app_category.dict','rb'))

	category_set = readCategory(category_id)
	tf(category_id,category_set,app_category_dict,app_tag_dict)

if __name__ == '__main__':
	main(15)









	