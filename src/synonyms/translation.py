#encoding=utf-8
import sys
sys.path.append('../common')
import text_process
import httplib
import urllib
import json
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import wordnet as wn

baidu_api = "openapi.baidu.com/public/2.0/bmt/translate?client_id=fIju3pgtaVlLvxCUu9c4HTAE&q=text&from=auto&to=auto"
youdao_api = "fanyi.youdao.com/openapi.do?keyfrom=zjulab&key=700725208&type=data&doctype=json&version=1.1&q=text"
host = "fanyi.youdao.com"
addr = "/openapi.do?keyfrom=zjulab&key=700725208&type=data&doctype=json&version=1.1&"

def getCandidateCategory(category_id):
	print 'reading category'
	category_set = set([])
	category_parent_dict = {}
	infile = open('../category/preprocess/candidate_category/'+str(category_id)+'.txt','rb')
	for row in infile:
		items = row.strip().split(',')
		word = items[0].decode('utf-8')
		if len(word) == 1:
			continue
		fre = int(items[1])
		category_set.add(word)
		category_parent_dict.setdefault(word,word)
	print '-category size: '+str(len(category_set))
	return category_set,category_parent_dict

def formatText(text):
	format_text = ""
	for val in text:
		if text_process.isChinese(val) or val == '[' or val == ']':
			continue
		format_text += val
	format_text = format_text.strip()
	return format_text

def findSynsetByWordnet(query_word):
	syn_set = set([])
	if len(query_word.split()) < 2:
		for synset in wn.synsets(query_word):
			for synset_item in synset.lemma_names():
				syn_set.add(' '.join(synset_item.split('_')))
	return syn_set

def translate(category_set):
	print 'translating online'
	st = LancasterStemmer()
	trans_category_dict = {}
	for category in category_set:
		params = {'q':category}
		query_encode = urllib.urlencode(params)
		conn = httplib.HTTPConnection(host)
		conn.request("GET", addr+query_encode)
		response = conn.getresponse()
		response_json = response.read()

		json_object = json.loads(response_json)

		if 'basic' in json_object.keys():
			basic_translation_list = json_object['basic']['explains']
			for basic_trans in basic_translation_list:
				basic_trans = formatText(basic_trans.decode('utf-8').lower())
				stem = st.stem(basic_trans)
				if len(stem) <= 2:
					trans_category_dict.setdefault(basic_trans,set([])).add(category)
				else:
					trans_category_dict.setdefault(stem,set([])).add(category)
				# for synset_item in findSynsetByWordnet(basic_trans):
				# 	trans_category_dict.setdefault(synset_item.lower(),set([])).add(category)

		if 'web' in json_object.keys():
			for web_trans in json_object['web']:
				if web_trans['key'] == category:
					for web_trans_item in web_trans['value']:
						web_trans_item = web_trans_item.decode('utf-8').lower()
						stem = st.stem(web_trans_item)				
						if len(stem) <= 2:
							trans_category_dict.setdefault(web_trans_item,set([])).add(category)
						else:
							trans_category_dict.setdefault(stem,set([])).add(category)
						# for synset_item in findSynsetByWordnet(web_trans_item):
						# 	trans_category_dict.setdefault(synset_item.lower(),set([])).add(category)

	return trans_category_dict

def mineSysnonyms(category_id,trans_category_dict,category_parent_dict):
	print 'mining sysnonyms'
	sysnonyms_set_dict = {}
	outfile = open('sysnonyms_'+str(category_id)+'.txt','wb')
	for trans in trans_category_dict.keys():
		category_list = list(trans_category_dict[trans])
		for i in range(len(category_list)):
			category_parent_dict[category_list[i]] = category_list[0]

	print '-aggregate category with same root'
	for category in category_parent_dict.keys():
		root = getRoot(category_parent_dict,category)
		sysnonyms_set_dict.setdefault(root,set([])).add(category)

	print '-writting'
	for sysnonyms_set in sysnonyms_set_dict.values():
		if len(sysnonyms_set) >= 2:
			outfile.write(' '.join(sysnonyms_set)+'\r\n')

def getRoot(category_parent_dict,category):
	if category_parent_dict[category] != category:
		return getRoot(category_parent_dict,category_parent_dict[category])
	else:
		return category


def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	category_set,category_parent_dict = getCandidateCategory(category_id)
	trans_category_dict = translate(category_set)

	for trans in trans_category_dict.keys():
		if len(trans_category_dict[trans]) == 1:
			continue
		print trans
		print ' '.join(trans_category_dict[trans])

	mineSysnonyms(category_id,trans_category_dict,category_parent_dict)

if __name__ == '__main__':
	category_id = 102228
	main(category_id)

