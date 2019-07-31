# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FeedItem(scrapy.Item):
    # required
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()

    # optional
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()