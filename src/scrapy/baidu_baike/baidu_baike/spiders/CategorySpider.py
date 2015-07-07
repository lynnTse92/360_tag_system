#encoding=utf-8
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from baidu_baike.items import CategoryItem
import chardet
import codecs
import os
import win32file

class CategorySpider(scrapy.spider.Spider):

	name = "baidu_baike_category"
	allowed_domains = ["baike.baidu.com"]
	# start_urls = [
	# 	u"http://baike.baidu.com/search?word=暗牌"
	# ]

	def start_requests(self):
		win32file._setmaxstdio(2048)
		infile = open('candidate_category_54.txt','rb')
		requests = []
		for row in infile:
			category = row.split(',')[0].decode('utf-8')
			outfile = open('54/raw/'+category,'wb')
			# outfile = os.fdopen('54/raw/'+category,'w')
			for page in range(10):
				request_url = u"http://baike.baidu.com/search?word="+category+"&pn="+str(page*10)
				print request_url
				requests.append(scrapy.FormRequest(request_url,callback=lambda response,outfile=outfile,category=category:self.parseCustom(response,outfile,category)))
		return requests

	def parse(self,response):
		print '***********************************'
		print 'parsing'
		print '***********************************'
		# outfile = open('test.txt','wb')
		for sel in response.xpath('//a[@class="result-title"]'):
			href = sel.xpath('@href').extract()[0]
			yield Request(url=href,callback=lambda response:self.parseItem(response))
			print href

	def parseCustom(self,response,outfile,category):
		print '***********************************'
		print 'parsing'
		print '***********************************'
		print category
		# with codecs.open(category, "wb",encoding='utf-8', errors='ignore') as outfile:
		for sel in response.xpath('//a[@class="result-title"]'):
			href = sel.xpath('@href').extract()[0]
			yield Request(url=href,callback=lambda response,outfile=outfile,category=category:self.parseItem(response,outfile,category))
			print href

	def parseItem(self,response,outfile,category):
		print '***********************************'
		print 'parsing item'
		print '***********************************'
		items = []
		item = CategoryItem()

		isEncodeUtf8 = True
		content_type = "utf-8"

		# content_type = chardet.detect(response.body)
		# print content_type

		# if content_type['encoding'] != "utf-8":
		# 	print content_type['encoding']
		# 	isEncodeUtf8 = False

		# outfile.write(response.body)

		#title
		main_title = ""
		main_title_note = ""
		for text in response.xpath('//span[@class="lemmaTitleH1"]'):
			if len(text.xpath('text()').extract()[0]) != 0:
				if isEncodeUtf8:
					main_title = text.xpath('text()').extract()[0].encode('utf-8').decode('utf-8','ignore')
				else:
					main_title = text.xpath('text()').extract()[0].decode(content_type,'ignore')
			if len(text.xpath('//sapn/text()').extract()) != 0:
				if isEncodeUtf8:
					main_title_note = text.xpath('//sapn/text()').extract()[0].encode('utf-8').decode('utf-8','ignore')
				else:
					main_title_note = text.xpath('//sapn/text()').extract()[0].decode(content_type,'ignore')
		item['category'] = category
		item['main_title'] = main_title
		item['main_title_note'] = main_title_note
		outfile.write(main_title+' '+main_title_note+'\r\n')
		
		#abstract
		abstract = ""
		for text in response.xpath('//div[@class="card-summary-content"]//div[@class="para"]/text()').extract():
			if isEncodeUtf8:
				abstract = text.encode('utf-8').decode('utf-8','ignore')
			else:
				abstract = text.decode(content_type,'ignore')
		item['abstract'] = abstract
		outfile.write(abstract+'\r\n')

		#tag info
		taginfo_dict = {}
		for text in response.xpath('//div[@class="baseInfoWrap"]//div[@class="biItem"]//div[@class="biItemInner"]'):
			tag = ""
			info = ""
			for text_item in text.xpath('span[@class="biTitle"]/text()').extract():
				if isEncodeUtf8:
					tag = text_item.encode('utf-8').decode('utf-8','ignore').replace(' ','')
				else:
					tag = text_item.decode(content_type,'ignore').replace(' ','')
			for text_item in text.xpath('div[@class="biContent"]/text()').extract():
				if isEncodeUtf8:
					info = text_item.encode('utf-8').decode('utf-8','ignore')
				else:
					info = text_item.decode(content_type,'ignore')
			taginfo_dict[tag] = info
		item['tag_infos'] = taginfo_dict
		outfile.write(' '.join(taginfo_dict.values())+'\r\n')

		#catalog
		catalog = []
		for text in response.xpath('//span[@class="headline-content"]/text()').extract():
			if isEncodeUtf8:
				catalog.append(text.encode('utf-8').decode('utf-8','ignore'))
			else:
				catalog.append(text.decode(content_type,'ignore'))
		item['catalog'] = catalog
		outfile.write(' '.join(catalog)+'\r\n')

		#content
		content = []
		for text in response.xpath('//div[@class="para"]/text()').extract():
			if isEncodeUtf8:
				content.append(text.encode('utf-8').decode('utf-8','ignore'))
				outfile.write(text.encode('utf-8').decode('utf-8','ignore')+'\r\n')
			else:
				content.append(text.decode(content_type,'ignore'))
				outfile.write(text.decode(content_type,'ignore')+'\r\n')				

		# item['content'] = content

		# items.append(item)
		# return items