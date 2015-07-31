#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import pickle
import jieba,jieba.posseg,jieba.analyse

data_path = '../../../data/'

def generateCandidateCategory(category_path):
	print 'loading file'
	jieba.load_userdict(data_path+"jieba_userdict.txt")
	stopword_set = text_process.getStopword('../../../data/stopword.txt')

	print 'reading file'
	word_title_dict = {}
	word_brief_dict = {}
	word_all_dict = {}
	infile = open('../data/'+category_path+'.json','rb')
	outfile = open('candidate_category/'+str(category_path)+'.txt','wb')
	for row in infile:
		json_obj = json.loads(row.strip())
		app_name = json_obj["soft_name"]
		app_brief = json_obj["soft_brief"]

		seg_title_list = jieba.cut(app_name)
		seg_brief_list = jieba.cut(app_brief)

		for seg_title in seg_title_list:
			if text_process.isChinese(seg_title) and seg_title not in stopword_set:
				word_title_dict.setdefault(seg_title,0)
				word_title_dict[seg_title] += 1

		for seg_brief in seg_brief_list:
			if text_process.isChinese(seg_brief) and seg_brief not in stopword_set: 
				word_brief_dict.setdefault(seg_brief,0)
				word_brief_dict[seg_brief] += 1

	print 'sorting'
	sorted_list = sorted(word_title_dict.items(),key=lambda p:p[1],reverse=True)
	for item in sorted_list:
		if item[1] >= 10:
			word_all_dict.setdefault(item[0],0)
			word_all_dict[item[0]] += item[1]
			# outfile.write(item[0]+','+str(item[1])+'\r\n')

	sorted_list = sorted(word_brief_dict.items(),key=lambda p:p[1],reverse=True)
	for item in sorted_list:
		if item[1] >= 50:
			word_all_dict.setdefault(item[0],0)
			word_all_dict[item[0]] += item[1]
			# outfile.write(item[0]+','+str(item[1])+'\r\n')

	sorted_list = sorted(word_all_dict.items(),key=lambda p:p[1],reverse=True)
	for item in sorted_list:
		outfile.write(item[0]+','+str(item[1])+'\r\n')

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	generateCandidateCategory(category_path)

if __name__ == '__main__':
	category_path = u"102232"
	main(category_path)

