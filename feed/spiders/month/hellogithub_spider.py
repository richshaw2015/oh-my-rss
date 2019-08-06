# -*- coding: utf-8 -*-

from feed.utils import *
from feed.items import *
import urllib


class HelloGithubSpider(scrapy.Spider):
    name = "hellogithub"
    start_urls = [
        'https://github.com/521xueweihan/HelloGitHub/blob/master/README.md',
    ]

    def parse(self, response):
        content_urls = response.xpath("//a[contains(text(),'第 ')]/@href").extract()[:3]

        if content_urls:
            for content_url in content_urls:
                full_url = urllib.parse.urljoin(self.start_urls[0], content_url)
                if not is_crawled_url(full_url):
                    yield response.follow(content_url, self.content_parse)
        else:
            self.logger.warning("Site has changed %s", self.name)

    def content_parse(self, response):
        title = response.xpath('//article//h1/text()').extract_first().strip()
        content = response.xpath('//article').extract_first()
        url = response.url
        yield FeedItem(title=title, content=content, url=url, name=self.name)
