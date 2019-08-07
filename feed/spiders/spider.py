from feed.utils import *
from feed.items import *
import urllib


class Spider(scrapy.Spider):
    """
    father class of article content spiders
    """

    def __init__(self, start_urls, index_xpath, article_title_xpath, article_content_xpath, article_trim_xpaths=None):
        self.start_urls = start_urls
        self.index_xpath = index_xpath
        self.article_title_xpath = article_title_xpath
        self.article_content_xpath = article_content_xpath
        self.article_trim_xpaths = article_trim_xpaths

    def parse(self, response):
        content_urls = response.xpath(self.index_xpath).extract()[:3]

        if content_urls:
            for content_url in content_urls:
                full_url = urllib.parse.urljoin(self.start_urls[0], content_url)
                if not is_crawled_url(full_url):
                    yield response.follow(content_url, self.content_parse)
        else:
            self.logger.error("Site maybe has changed %s", self.name)

    def content_parse(self, response):
        title = response.xpath(self.article_title_xpath).extract_first().strip()
        content = response.xpath(self.article_content_xpath).extract_first()
        url = response.url
        yield FeedItem(title=title, content=content, url=url, name=self.name, trims=self.article_trim_xpaths)
