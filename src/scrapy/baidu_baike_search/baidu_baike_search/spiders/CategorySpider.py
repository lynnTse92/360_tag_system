#encoding=utf-8
import scrapy
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
from scrapy.http import Request
from baidu_baike_search.items import BaiduBaikePageItem

class CategorySpider(BaseSpider):

	name = "baidu_baike_search"
	allowed_domains = ["baike.baidu.com"]

	input_name = u"17"
	page_size = 10
	page_num = 5

	def start_requests(self):
		infile = open('../../category/preprocess/candidate_category/'+self.input_name+'.txt','rb')
		requests = []
		for row in infile:
			category = row.split(',')[0].decode('utf-8')
			print category
			for offset in range(self.page_num):
				request_url = u"http://baike.baidu.com/search?word="+category+"&pn="+str(offset*self.page_size)
				requests.append(scrapy.FormRequest(request_url,meta={'offset':str(offset)},callback=lambda response,category=category:self.parseSearchPage(response,category)))
		return requests

	def parseSearchPage(self,response,category):
		for sel in response.xpath('//a[@class="result-title"]'):
			url = sel.xpath('@href').extract()[0]
			yield Request(url=url,meta={'offset':str(response.meta['offset'])},callback=lambda response,category=category:self.parseDetailPage(response,category))

	def parseDetailPage(self,response,category):
		item = BaiduBaikePageItem()
		item['query_category'] = category
		item['offset'] = response.meta['offset']

		#title
		title = ''.join(response.xpath('//span[@class="lemmaTitleH1"]//text()').extract()).encode('utf-8')
		item['title'] = title
		
		#abstract
		abstract = ''.join(response.xpath('//div[@class="card-summary-content"]//div[@class="para"]//text()').extract()).encode('utf-8')
		abstract_link = ''.join(response.xpath('//div[@class="card-summary-content"]//div[@class="para"]//a//text()').extract()).encode('utf-8')
		abstract_bold = ''.join(response.xpath('//div[@class="card-summary-content"]//div[@class="para"]//b//text()').extract()).encode('utf-8')
		item['abstract'] = abstract
		item['abstract_link'] = abstract_link
		item['abstract_bold'] = abstract_bold

		#baidu tags
		item['tags'] = response.xpath('//div[@class="baseInfoWrap"]//div[@class="biItem"]//div[@class="biItemInner"]//div[@class="biContent"]//text()').extract()
	
		#content
		item['content'] = ''.join(response.xpath('//div[@class="para"]//text()').extract()).encode('utf-8')
		item['content_link'] = ''.join(response.xpath('//div[@class="para"]//a//text()').extract()).encode('utf-8')
		item['content_bold'] = ''.join(response.xpath('//div[@class="para"]//bold//text()').extract()).encode('utf-8')				

		return item


