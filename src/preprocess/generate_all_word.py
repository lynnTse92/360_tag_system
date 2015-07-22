#encoding=utf-8
import sys
sys.path.append('../common')
import text_process
import json
import pickle
import jieba,jieba.posseg,jieba.analyse

def readSegFile():
	infile = open('../../data/all_cn_seg_nwi_clean.txt','rb')
	outfile = open('../../data/all_word.txt','wb')
	stopword_set = text_process.getStopword('../../data/stopword.txt')
	word_set = set([])
	row_counter = 0
	for row in infile:
		row_counter += 1
		print row_counter
		row = row.strip().decode('utf-8')
		items = row.split('<@>')
		app_name = items[1]
		brief_seg = items[2].split()
		title_seg = jieba.cut(app_name)
		for title in title_seg:
			if text_process.isChinese(title) and title not in stopword_set:
				word_set.add(title)
		for brief in brief_seg:
			word_set.add(brief)
	for word in word_set:
		outfile.write(word+'\r\n')


def main():
	reload(sys)
	sys.setdefaultencoding('utf-8')

	readSegFile()

if __name__ == '__main__':
	main()











