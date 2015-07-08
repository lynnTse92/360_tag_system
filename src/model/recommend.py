#encoding=utf-8
import sys
import pickle
import jieba,jieba.posseg,jieba.analyse

data_path = '../../data/'

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

#判断shorter_text是否被longer_text包含
def isSubset(shorter_text,longer_text):
	is_subset = False
	for i in range(len(longer_text)):	
		if shorter_text == ''.join(longer_text[i:i+len(shorter_text)]):
			is_subset = True
		if i+len(shorter_text) == len(longer_text):
			break
	return is_subset

def getCategoryTagSet(category_id):
	category_tag_set = set([])
	infile = open('../category/model/tag_set_'+str(category_id)+'.txt','rb')
	for row in infile:
		category_tag_set.add(row.strip().decode('utf-8'))
	return category_tag_set

def combine(tag_set):
	tag_list = list(tag_set)
	for tag_i in tag_list:
		for tag_j in tag_list:
			if tag_i != tag_j:
				if len(tag_i) < len(tag_j):
					if isSubset(tag_i,tag_j):
						if tag_i in tag_set:
							tag_set.remove(tag_i)
	return tag_set

def recommend(category_id,category_tag_set):
	print 'loading file'
	jieba.load_userdict(data_path+"jieba_userdict.txt")
	app_tag_dict = pickle.load(open(data_path+'app_tag.dict','rb'))
	app_category_dict = pickle.load(open(data_path+'app_category.dict','rb'))

	print 'reading app'
	infile = open(data_path+'all_cn_seg_nwi_clean.txt','rb')
	outfile = open('app_recommend_tag'+str(category_id)+'.txt','wb')
	for row in infile:
		app_recommend_tag = set([])
		app_recommend_tag2 = set([])
		word_fre_dict = {}
		items = row.strip().split("<@>")
		try:
			app_id = int(items[0])
			app_name = items[1].decode('utf-8')
			seg_brief_list = items[2].decode('utf-8').split()
		except:
			continue
		if app_category_dict[app_id][1] != category_id:
			continue

		seg_title_list = jieba.cut(app_name)
		for seg_title in seg_title_list:
			word_fre_dict.setdefault(seg_title,0)
			word_fre_dict[seg_title] += 1
			if seg_title in category_tag_set:
				app_recommend_tag.add(seg_title)
		for seg_brief in seg_brief_list:
			word_fre_dict.setdefault(seg_brief,0)
			word_fre_dict[seg_brief] += 1
			if seg_brief in category_tag_set:
				app_recommend_tag.add(seg_brief)
		sorted_list = sorted(word_fre_dict.items(),key=lambda p:p[1],reverse=True)
		for val in sorted_list[:8]:
			if val[0] in category_tag_set:
				app_recommend_tag2.add(val[0])
		# for word in word_fre_dict.keys():
		# 	if word_fre_dict[word] >= 2 and word in category_tag_set:
		# 		app_recommend_tag2.add(word)
		app_recommend_tag2 = combine(app_recommend_tag2) 
		app_recommend_tag = combine(app_recommend_tag)
		outfile.write(str(app_id)+'<@>'+app_name+'<@>'+' '.join(app_recommend_tag2)+'<@>'+' '.join(app_recommend_tag)+'<@>'+' '.join(app_tag_dict[app_id])+'\r\n')


def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	category_tag_set = getCategoryTagSet(category_id)
	recommend(category_id,category_tag_set)

if __name__ == '__main__':
	main(102232)

