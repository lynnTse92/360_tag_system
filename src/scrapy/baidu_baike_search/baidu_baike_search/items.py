# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduBaikePageItem(scrapy.Item):
    #查询的候选类目词
    query_category = scrapy.Field()
    #查询偏移量
    offset = scrapy.Field()
    #标题
    title = scrapy.Field()
    #标题备注
    title_note = scrapy.Field()
    #摘要
    abstract = scrapy.Field()
    #摘要中的链接
    abstract_link = scrapy.Field()
    #摘要中的粗体
    abstract_bold = scrapy.Field()
    #正文内容
    content = scrapy.Field()
    #正文内容中的链接
    content_link = scrapy.Field()
    #正文内容中的粗体
    content_bold = scrapy.Field()
    #百度标签
    tags = scrapy.Field()
