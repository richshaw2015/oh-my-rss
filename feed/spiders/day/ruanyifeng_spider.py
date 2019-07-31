# -*- coding: utf-8 -*-

from feed.utils import *
from feed.items import *


class RuanyifengSpider(scrapy.Spider):
    name = "ruanyifeng"
    start_urls = [
        'http://www.ruanyifeng.com/blog/',
    ]

    def parse(self, response):
        content_urls = response.xpath('//div[@class="asset-header"]/h2/a/@href').extract()[:2]
        # content_urls = response.xpath('//*[@class="module-list-item"]//a/@href').extract()[:20]
        if content_urls:
            for content_url in content_urls:
                full_url = urllib.parse.urljoin(self.start_urls[0], content_url)
                if not is_crawled_url(full_url):
                    yield response.follow(content_url, self.content_parse)
        else:
            # TODO 页面改版的异常处理
            self.logger.warning("%s", self.name)

    def content_parse(self, response):
        title = response.xpath('//*[@id="page-title"]/text()').extract_first().strip()
        content = response.xpath('//*[@id="main-content"]').extract_first()
        url = response.url
        yield FeedItem(title=title, content=content, url=url, name=self.name)
