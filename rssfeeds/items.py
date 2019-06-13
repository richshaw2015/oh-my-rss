# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RssfeedsItem(scrapy.Item):
    # 必填
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()

    # 选填，下载防盗链的图片
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()