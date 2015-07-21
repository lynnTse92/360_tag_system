# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduBaikePageItem(scrapy.Item):
    query_category = scrapy.Field()
    offset = scrapy.Field()
    title = scrapy.Field()
    title_note = scrapy.Field()
    abstract = scrapy.Field()
    abstract_link = scrapy.Field()
    abstract_bold = scrapy.Field()
    content = scrapy.Field()
    content_link = scrapy.Field()
    content_bold = scrapy.Field()
    tags = scrapy.Field()
    pass
