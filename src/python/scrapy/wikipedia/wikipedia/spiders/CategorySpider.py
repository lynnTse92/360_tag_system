#encoding=utf-8
import scrapy
from scrapy.http import Request
from wikipedia.items import CategoryItem
import json
import copy

class CategorySpider(scrapy.spider.Spider):

	recursive_max = 3
	outfile = open('category_path.json','wb')

	name = "wikipedia_category"
	domain = "https://zh.wikipedia.org"
	start_urls = [
		u"https://zh.wikipedia.org/wiki/Wikipedia:%E5%88%86%E9%A1%9E%E7%B4%A2%E5%BC%95"
	]

	def parse(self,response):
		for link_element in response.xpath('//div[@class="mw-content-ltr"]//a[contains(@title, "Category:")]'):
			url = self.domain+link_element.xpath('.//@href').extract()[0]
			category = link_element.xpath('.//text()').extract()[0]
			url = unicode(url)
			category_path_text = category+"<@>"
			yield Request(url=url,meta={'category_path_text':category_path_text},callback=self.parseItem)
			break

	def parseItem(self,response):
		category_path_text = response.meta['category_path_text']
		isLast = True
		for link_element in response.xpath('//div[@class="mw-content-ltr"]//a[@class="CategoryTreeLabel  CategoryTreeLabelNs14 CategoryTreeLabelCategory"]'):
			isLast = False
			url = self.domain+link_element.xpath('.//@href').extract()[0]
			category = link_element.xpath('.//text()').extract()[0]
			if len(category_path_text.split('<@>'))+1 == self.recursive_max:
				final_category_path = category_path_text+category
				# print final_category_path
				self.outfile.write(json.dumps(final_category_path.split('<@>'))+'\r\n')
			else:
				new_category_path_text = category_path_text+category+"<@>"
				yield Request(url=url,meta={'category_path_text': new_category_path_text},callback=self.parseItem)
		for sub_category in response.xpath('//div[@id="mw-pages"]//a/text()').extract():
			addition_category_path = category_path_text+sub_category
			self.outfile.write(json.dumps(addition_category_path.split('<@>'))+'\r\n')
		
		if isLast:
			self.outfile.write(json.dumps(category_path_text.split('<@>'))+'\r\n')


