#encoding=utf-8
import sys
sys.path.append("../../common/")
import os
import text_process
import file_utils
import common
import jieba,jieba.posseg,jieba.analyse

data_path = '../../../data/'

def extractFeatureFromWikiCategory(category_id,relevant_category_list,category_set):
	print 'extracting feature from wikipedia category'
	infile = open('../../scrapy/wikipedia/category_path_clean.txt','rb')
	outfile = open('wikipedia/'+str(category_id)+'.csv','wb')
	category_feature_dict = {}
	for category in category_set:
		category_feature_dict.setdefault(category,[0,0,[],set([])])
	max_cover_num = 0
	row_index = 0
	for row in infile:
		row_index += 1
		# print row_index
		words = row.strip().split(',')
		words = [word.decode('utf-8') for word in words]
		level = 1
		handled_word_set = set([])
		for i in range(len(words)):
			word = words[i].decode('utf-8')
			
			isRelevant = False
			for relevant_category in relevant_category_list:
				if relevant_category in row.strip().decode('utf-8'):
					isRelevant = True
					break

			# seg_word_list = jieba.cut(word)
			# for seg_word in seg_word_list:
			# 	if seg_word in category_set and seg_word not in handled_word_set:
			# 		category_feature_dict[seg_word][0] = 1
			# 		if isRelevant:
			# 			category_feature_dict[seg_word][1] = 1
			# 		category_feature_dict[seg_word][2].append(level)
			# 		handled_word_set.add(seg_word)

			# 		other_words_set = set([])
			# 		if i+1 != len(words):
			# 			for other_word in words[i+1]:
			# 				other_seg_word_list = jieba.cut(other_word)
			# 				for other_seg_word in other_seg_word_list:
			# 					other_words_set.add(other_seg_word)

			# 		cover_set = other_words_set & category_set - handled_word_set
			# 		category_feature_dict[seg_word][3] = category_feature_dict[seg_word][3] | cover_set 
			# 		if len(category_feature_dict[seg_word][3]) > max_cover_num:
			# 			max_cover_num = len(category_feature_dict[seg_word][3])

			# if len(set(jieba.cut(word)) & category_set) >= 1:
			# 	level += 1

			if word in category_set and word not in handled_word_set:
				category_feature_dict[word][0] = 1
				if isRelevant:
					category_feature_dict[word][1] = 1
				category_feature_dict[word][2].append(level)
				handled_word_set.add(word)

				other_words_set = set([])
				if i+1 != len(words):
					for other_word in words[i+1]:
						other_words_set.add(other_word)

				cover_set = other_words_set & category_set - handled_word_set
				category_feature_dict[word][3] = category_feature_dict[word][3] | cover_set 
				if len(category_feature_dict[word][3]) > max_cover_num:
					max_cover_num = len(category_feature_dict[word][3])

			if word in category_set:
				level += 1

		# if row_index == 10000:
		# 	break

	print 'writing'
	for category in category_feature_dict.keys():
		is_in_wiki = category_feature_dict[category][0]
		is_relevant = category_feature_dict[category][1]
		average_level_in_wiki = 0
		if len(category_feature_dict[category][2]) != 0:
			average_level_in_wiki = 1.0*sum(category_feature_dict[category][2])/(10*len(category_feature_dict[category][2]))
		cover_num = 1.0*len(category_feature_dict[category][3])/max_cover_num
		outfile.write(category+','+str(is_in_wiki)+','+str(is_relevant)+','+str(average_level_in_wiki)+','+str(cover_num)+'\r\n')

#1.is_in_wiki
#2.is_relevant
#3.average_level_in_wiki
#4.cover_num

def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	jieba.load_userdict(data_path+"jieba_userdict.txt")
	file_utils.createDirs(['wikipedia'])
	relevant_category_list = [u'棋',u'牌',u'牌类',u'棋类',u'纸牌']
	# relevant_category_list = [u'阅读',u'新闻',u'读书',u'资讯']
	# relevant_category_list = [u'教育',u'学习']
	# relevant_category_list = [u'摄影',u'摄像']

	category_set = common.getCandidateCategory(category_id)
	extractFeatureFromWikiCategory(category_id,relevant_category_list,category_set)

if __name__ == '__main__':
	category_id = int(sys.argv[1])
	main(category_id)
