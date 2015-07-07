# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CategoryItem(scrapy.Item):
    # define the fields for your item here like:
    category = scrapy.Field()
    main_title = scrapy.Field()
    main_title_note = scrapy.Field()
    abstract = scrapy.Field()
    tag_infos = scrapy.Field()
    catalog = scrapy.Field()
    content = scrapy.Field()
