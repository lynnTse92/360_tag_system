#encoding=utf-8
import sys
import pickle
import jieba,jieba.posseg,jieba.analyse

data_path = '../../../data/'

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

def generateCandidateCategory(category_id):
	print 'loading file'
	jieba.load_userdict(data_path+"jieba_userdict.txt")
	app_tag_dict = pickle.load(open(data_path+'app_tag.dict','rb'))
	app_category_dict = pickle.load(open(data_path+'app_category.dict','rb'))
	stopword_set = getStopword()

	print 'reading file'
	word_fre_dict = {}
	infile = open(data_path+'all_cn_seg_nwi_clean.txt','rb')
	outfile = open('candidate_category/'+str(category_id)+'.txt','wb')
	for row in infile:
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
			if isChinese(seg_title) and seg_title not in stopword_set:
				word_fre_dict.setdefault(seg_title,0)
				word_fre_dict[seg_title] += 1

		# for seg_brief in seg_brief_list:
		# 	if isChinese(seg_brief):
		# 		word_fre_dict.setdefault(seg_brief,0)
		# 		word_fre_dict[seg_brief] += 1

		# for tag in app_tag_dict[app_id]:
		# 	seg_tag_list = jieba.cut(tag)
		# 	for seg_tag in seg_tag_list:
		# 		if isChinese(seg_tag) and seg_tag not in stopword_set:
		# 			word_fre_dict.setdefault(seg_tag,0)
		# 			word_fre_dict[seg_tag] += 1
				
	print 'sorting'
	sorted_list = sorted(word_fre_dict.items(),key=lambda p:p[1],reverse=True)
	for item in sorted_list:
		if item[1] >= 10:
			outfile.write(item[0]+','+str(item[1])+'\r\n')


def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	generateCandidateCategory(category_id)

if __name__ == '__main__':
	main(51)

