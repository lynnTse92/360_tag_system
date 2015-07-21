#encoding=utf-8
import sys
import json
import jieba
import jieba.posseg as pseg
import jieba.analyse
from scrapy.selector import Selector

def readJson(category_path):
	print 'reading json'
	json_str = ""
	infile = open('../crawl_data/'+category_path+'.json',"rb")
	outfile = open('../clean_data/'+category_path+'.json',"wb")
	row_index = 0
	for row in infile:
		row_index += 1
		print row_index
		json_str = row.strip()
		json_str = json_str.replace('[','')
		json_str = json_str.rstrip(',')
		json_str = json_str.replace(']','')
		try:
			wiki_page_dict = {}
			json_obj = json.loads(json_str)
			print json_obj['query_category']

			#################### query_category ####################
			wiki_page_dict['query_category'] = json_obj['query_category']
			#################### query_category ####################

			#################### offset ####################
			wiki_page_dict['offset'] = json_obj['offset']
			#################### offset ####################
			
			#################### wiki_category ####################
			wiki_page_dict['wiki_category'] = Selector(text=json_obj['content']).xpath('//div[@class="mw-normal-catlinks"]//li//a//text()').extract()
			#################### wiki_category ####################

			#################### abstract ####################
			abstract_raw_text = ""
			if len(json_obj['content'].split('<h2>')) >= 2:
				abstract_raw_text = json_obj['content'].split('<h2>')[0]
			else:
				abstract_raw_text = json_obj['content']
			wiki_page_dict['abstract'] = ''.join(Selector(text=abstract_raw_text).xpath('//p//text()').extract())
			wiki_page_dict['abstract_link'] = Selector(text=abstract_raw_text).xpath('//p//a//text()').extract()
			wiki_page_dict['abstract_bold'] = Selector(text=abstract_raw_text).xpath('//p//b//text()').extract()
			#################### abstract ####################

			#################### content ####################
			if len(json_obj['content'].split('<h2>')) >= 2:
				content_raw_text = ''.join(json_obj['content'].split('<h2>')[1:])

				wiki_page_dict['content'] = ''.join(Selector(text=content_raw_text).xpath('//text()').extract())
				wiki_page_dict['content_link'] = Selector(text=content_raw_text).xpath('//a//text()').extract()
				wiki_page_dict['content_bold'] = Selector(text=content_raw_text).xpath('//b//text()').extract()
			#################### content ####################		
			outfile.write(json.dumps(wiki_page_dict)+'\r\n')
		except:
			print 'opps'
	

def main(category_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	json_object = readJson(category_path)

if __name__ == '__main__':
	category_path = u"17_笔记备忘"
	main(category_path)
	