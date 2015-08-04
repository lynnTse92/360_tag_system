#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import pickle
import jieba,jieba.posseg,jieba.analyse
import itertools

def readWikipediaCategoryPath(query):
	print 'reading wikipedia category path'
	outfile = open('../wiki_query_result.txt','wb')
	infile = open('../../scrapy/wikipedia/category_path_clean.txt','rb')
	row_counter = 0
	for row in infile:
		row = row.strip().decode('utf-8')
		row_counter += 1
		print row_counter
		if query in row:
			outfile.write(row+'\r\n')
			


def main():
	reload(sys)
	sys.setdefaultencoding('utf-8')

	query = u"金融"
	readWikipediaCategoryPath(query)


if __name__ == '__main__':
	main()











