# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Product(scrapy.Item):
    ProductID = scrapy.Field()
    ProductName = scrapy.Field()
    ProductPrice = scrapy.Field()
    ProductLink = scrapy.Field()
    ImgLink = scrapy.Field()
    Category = scrapy.Field()
    CreationTime = scrapy.Field()
    ExpirationTime = scrapy.Field()
