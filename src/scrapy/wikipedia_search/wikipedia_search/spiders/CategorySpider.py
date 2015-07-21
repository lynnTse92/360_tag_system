#encoding=utf-8
import scrapy
from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
from wikipedia_search.items import WikipediaPageItem
import urllib

class CategorySpider(BaseSpider):

	name = "wikipedia_search"
	host = "https://zh.wikipedia.org"
	input_name = u'17_笔记备忘'
	page_size = 10
	page_num = 5

	def start_requests(self):
		infile = open('data/candidate_category/'+self.input_name+'.txt','rb')
		requests = []
		for row in infile:
			category = row.split(',')[0].decode('utf-8')
			for offset in range(self.page_num):
				request_url = u"https://zh.wikipedia.org/w/index.php?limit="+str(self.page_size)+"&offset="+str(offset)+"&fulltext=Search&search="+category
				requests.append(scrapy.FormRequest(request_url,meta={'offset':str(offset)},callback=lambda response,category=category:self.parseSearchPage(response,category)))
		return requests

	def parseSearchPage(self,response,category):
		print category
		offset = response.meta['offset']
		for sel in response.xpath('//div[@class="mw-search-result-heading"]'):
			href = sel.xpath('a//@href').extract()[0]
			url = self.host+href
			yield Request(url=url,meta={'offset':str(offset)},callback=lambda response,category=category:self.parseDetailPage(response,category))

	def parseDetailPage(self,response,category):
		item = WikipediaPageItem()

		item['query_category'] = category
		item['title'] = response.xpath('//h1[@class="firstHeading"]//text()').extract()[0]
		item['offset'] = response.meta['offset']
		item['content'] = response.xpath('//div[@class="mw-body-content"]').extract()[0]

		return item




