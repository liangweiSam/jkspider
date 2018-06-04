# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RmfyggSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    court = scrapy.Field()
    noticeCode = scrapy.Field()
    noticeContent = scrapy.Field()
    noticeType = scrapy.Field()
    payStatus = scrapy.Field()
    publishDate = scrapy.Field()
    tosendPeople = scrapy.Field()
    uuid = scrapy.Field()
