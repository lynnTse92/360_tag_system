#encoding=utf-8
import sys

#判断shorter_text是否被longer_text包含
def isSubset(shorter_text,longer_text):
	is_subset = False
	for i in range(len(longer_text)):	
		if shorter_text == ''.join(longer_text[i:i+len(shorter_text)]):
			is_subset = True
		if i+len(shorter_text) == len(longer_text):
			break
	return is_subset

def readCandidateCategory(category_id):
	print 'reading candidate category'
	category_feature_dict = {}
	infile = open('../../data/candidate_concept_title_'+str(category_id)+'.txt','rb')
	for row in infile:
		items = row.strip().split(',')
		word = items[0].decode('utf-8')
		fre = int(items[1])
		category_feature_dict.setdefault(word,[0,[],[],0])
	return category_feature_dict

def extractFeatureFromWikiCategory(category_id,relevant_category_list,category_feature_dict):
	print 'extracting feature from wikipedia category'
	infile = open('../../data/category_path_clean.txt','rb')
	outfile = open('feature/category_feature_wiki_'+str(category_id)+'.csv','wb')
	category_set = set(category_feature_dict.keys())
	max_cover_num = 0
	row_index = 0
	for row in infile:
		row_index += 1
		print row_index
		words = row.strip().split(',')
		words = [word.decode('utf-8') for word in words]
		level = 1
		for i in range(len(words)):
			word = words[i].decode('utf-8')
			if word in category_set:
				category_feature_dict[word][0] = 1
				category_feature_dict[word][1].append(level)
				level += 1
				if i+1 != len(words):
					other_words_set = set([val.decode('utf-8') for val in words[i+1:]])
					cover_num = len(category_set & other_words_set)
					category_feature_dict[word][3] += cover_num
					if category_feature_dict[word][3] > max_cover_num:
						max_cover_num = category_feature_dict[word][3]
			isRelevant = False
			if len(set(relevant_category_list) & set(words)) >= 1:
				isRelevant = True
			if isRelevant and word in category_set:
				category_feature_dict[word][2].append(level)

	print 'writing'
	for category in category_feature_dict.keys():
		is_in_wiki = category_feature_dict[category][0]
		average_level_in_wiki = 0
		if len(category_feature_dict[category][1]) != 0:
			average_level_in_wiki = 1.0*sum(category_feature_dict[category][1])/(8*len(category_feature_dict[category][1]))
		average_relation_level_in_wiki = 0
		if len(category_feature_dict[category][2]) != 0:
			average_relation_level_in_wiki = 1.0*sum(category_feature_dict[category][2])/(8*len(category_feature_dict[category][2]))
		cover_num = 1.0*category_feature_dict[category][3]/max_cover_num
		outfile.write(category+','+str(is_in_wiki)+','+str(average_level_in_wiki)+','+str(average_relation_level_in_wiki)+','+str(cover_num)+'\r\n')

#1.is_in_wiki
#2.average_level_in_wiki
#3.average_relation_level_in_wiki
#4.cover_num

def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	# relevant_category_list = [u'棋',u'牌',u'牌类',u'棋类',u'纸牌']
	relevant_category_list = [u'阅读',u'新闻',u'读书',u'资讯']
	category_feature_dict = readCandidateCategory(category_id)
	extractFeatureFromWikiCategory(category_id,relevant_category_list,category_feature_dict)

if __name__ == '__main__':
	main(15)