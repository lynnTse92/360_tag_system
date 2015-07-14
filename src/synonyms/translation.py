#encoding=utf-8
import sys
import httplib
import urllib
import json
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import wordnet

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

def translate(category_set):
	print 'translating online'
	st = LancasterStemmer()
	category_trans_dict = {}
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
			translation_list = json_object['basic']['explains']
			category_trans_dict.setdefault(category,translation_list)
			for trans in translation_list:
				trans = trans.decode('utf-8')
				stem = st.stem(trans)
				trans_category_dict.setdefault(trans,set([])).add(category)
		else:
			category_trans_dict.setdefault(category,[])
	return trans_category_dict

def mineSysnonyms(category_id,trans_category_dict,category_parent_dict):
	print 'mining sysnonyms'
	sysnonyms_set_dict = {}
	outfile = open('sysnonyms_'+str(category_id)+'.txt','wb')
	for trans in trans_category_dict.keys():
		category_list = list(trans_category_dict[trans])
		for i in range(len(category_list)):
			category_parent_dict[category_list[i]] = category_list[0]

	print '-aggregate with same root'
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
	mineSysnonyms(category_id,trans_category_dict,category_parent_dict)

if __name__ == '__main__':
	category_id = 102228
	main(category_id)

