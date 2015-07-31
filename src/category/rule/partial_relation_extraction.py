#encoding=utf-8
import sys
sys.path.append('../../common')
import text_process
import json
import pickle
import jieba,jieba.posseg,jieba.analyse
import itertools

def getLocationCategorySet():
	print 'getting comment category'
	location_category_set = set([])
	infile = open('../data/location.txt','rb')
	for row in infile:
		location_category_set.add(row.strip().decode('utf-8'))
	return location_category_set

def getCategorySet(category_path):
	print 'getting category set'
	category_set = set([])
	# infile = open('../../../data/54.txt','rb')
	# for row in infile:
	# 	category = row.strip().decode('utf-8').split(',')[0]
	# 	category_set.add(category)
	category_set.add(u'购物')
	category_set.add(u'教育')
	category_set.add(u'社交')
	category_set.add(u'体育')

	return category_set

def readWikipediaCategoryPath(category_set,location_category_set):
	print 'reading wikipedia category path'
	outfile = open('../data/partial.txt','wb')
	infile = open('../../scrapy/wikipedia/category_path_clean.txt','rb')
	row_counter = 0
	pair_set = set([])
	for row in infile:
		row_counter += 1
		print row_counter
		# if row_counter >= 10000:
		# 	break
		cover_pairwise_list = []
		category_path_list = row.strip().decode('utf-8').split(',')
		if len(category_set & set(category_path_list)):
			for category in category_path_list:
				cover_pairwise_list.append(category)
		if len(cover_pairwise_list) >= 2:
			pair_list = list(itertools.combinations(cover_pairwise_list,2))
			for pair in pair_list:
				if pair[0] != pair[1]:
					pair_set.add(pair)
	
	for pair in pair_set:
		outfile.write('>'.join(pair)+'\r\n')
			


def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	location_category_set = getLocationCategorySet()
	category_set = getCategorySet(category_path)
	readWikipediaCategoryPath(category_set,location_category_set)


if __name__ == '__main__':

	category_path = u"17"
	main(category_path)











