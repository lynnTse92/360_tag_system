#encoding=utf-8
import sys
import pickle
import jieba,jieba.posseg,jieba.analyse

def isChinese(var):
	for v in var:
		if not(0x4e00<=ord(v)<0x9fa6):
			return False
	return True

#判断shorter_text是否被longer_text包含
def isSubset(shorter_text,longer_text):
	is_subset = False
	for i in range(len(longer_text)):	
		if shorter_text == ''.join(longer_text[i:i+len(shorter_text)]):
			is_subset = True
		if i+len(shorter_text) == len(longer_text):
			break
	return is_subset

def getStopword():
	infile = '../../data/stopword.txt'
	stopword_set = set()
	infile = open(infile, 'rb')
	for line in infile:
		stopword_set.add(line.strip().decode('utf-8'))
	infile.close()
	return stopword_set

def readCandidateCategory(category_id):
	print 'reading candidate category'
	category_feature_dict = {}
	infile = open('../../data/candidate_concept_title_'+str(category_id)+'.txt','rb')
	for row in infile:
		items = row.strip().split(',')
		word = items[0].decode('utf-8')
		fre = int(items[1])
		category_feature_dict.setdefault(word,0)
	return category_feature_dict

def inclusionRelation(category_feature_dict):
	print 'extracting inclusion relation feature'
	outfile = open('feature/inclusion_54.csv','wb')
	for i in range(len(category_feature_dict.keys())):
		word_i = category_feature_dict.keys()[i]
		for j in range(len(category_feature_dict.keys())):
			word_j = category_feature_dict.keys()[j]
			if len(word_i) >= 4 and len(word_j) >= 4:
				continue
			if i>j:		
				if len(word_i) <= len(word_j):
					if isSubset(word_i,word_j):
						category_feature_dict[word_i] += 1
				else:
					if isSubset(word_j,word_i):
						category_feature_dict[word_j] += 1
	inclusion_max = max(category_feature_dict.values())
	print 'sorting'
	sorted_list = sorted(category_feature_dict.items(),key=lambda p:p[1],reverse=True)
	print 'writing'
	for val in sorted_list:
		inclusion_normalize = 1.0*val[1]/inclusion_max
		outfile.write(val[0]+','+str(inclusion_normalize)+'\r\n')

def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	category_feature_dict = readCandidateCategory(category_id)
	inclusionRelation(category_feature_dict)

if __name__ == '__main__':
	main(54)