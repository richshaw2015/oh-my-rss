from feed.utils import *
from feed.items import *
import urllib


class Spider(scrapy.Spider):
    """
    father class of article content spiders
    """

    def __init__(self, start_urls, index_xpath, article_title_xpath, article_content_xpath, article_trim_xpaths=None,
                 index_limit_count=None, index_reverse=False, browser=False):
        self.start_urls = start_urls
        self.index_xpath = index_xpath
        self.article_title_xpath = article_title_xpath
        self.article_content_xpath = article_content_xpath
        self.article_trim_xpaths = article_trim_xpaths
        self.index_limit_count = index_limit_count
        self.index_reverse = index_reverse
        self.browser = browser

    def parse(self, response):
        content_urls = response.xpath(self.index_xpath).extract()

        if self.index_reverse:
            content_urls.reverse()

        if self.index_limit_count:
            content_urls = content_urls[:self.index_limit_count]

        if content_urls:
            for content_url in content_urls:
                full_url = urllib.parse.urljoin(self.start_urls[0], content_url)
                if not is_crawled_url(full_url):
                    self.logger.error(f"Begin crawl`{full_url}")
                    yield response.follow(content_url, self.content_parse)
        else:
            self.logger.error("Site maybe has changed`%s", self.name)

    def content_parse(self, response):
        try:
            title = response.xpath(self.article_title_xpath).extract_first().strip()
            content = response.xpath(self.article_content_xpath).extract_first()
        except AttributeError:
            self.logger.warning("Xpath Error`%s`%s", response.url, response.body.decode('utf8'))
        url = response.url
        try:
            req_url = response.meta['redirect_urls'][0]
        except KeyError:
            req_url = url
        yield FeedItem(title=title, content=content, url=url, name=self.name, trims=self.article_trim_xpaths,
                       req_url=req_url)
