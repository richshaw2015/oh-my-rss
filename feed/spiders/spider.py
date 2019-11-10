from feed.utils import *
from feed.items import *
import urllib


class Spider(scrapy.Spider):
    """
    father class of article content spiders
    """

    def __init__(self, start_urls, index_xpath, article_title_xpath, article_content_xpath, article_trim_xpaths=None,
                 index_limit_count=None, index_reverse=False, browser=False, css=None, trim_style_tags=None):
        self.start_urls = start_urls
        self.index_xpath = index_xpath
        self.article_title_xpath = article_title_xpath
        self.article_content_xpath = article_content_xpath
        self.article_trim_xpaths = article_trim_xpaths
        self.index_limit_count = index_limit_count
        self.index_reverse = index_reverse
        self.browser = browser
        self.css = css
        self.trim_style_tags = trim_style_tags

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
                    self.logger.info(f"Begin crawl`{full_url}")
                    yield response.follow(content_url, self.content_parse)
        else:
            self.logger.error("Site maybe has changed`%s", self.name)

    def content_parse(self, response):
        try:
            title = response.xpath(self.article_title_xpath).extract_first().strip()[:100]
            content = response.xpath(self.article_content_xpath).extract_first()
        except AttributeError:
            self.logger.warning("Xpath Error`%s", response.url)
            return False
        url = response.url
        try:
            req_url = response.meta['redirect_urls'][0]
        except KeyError:
            req_url = url
        yield FeedItem(title=title, content=content, url=url, name=self.name, trims=self.article_trim_xpaths,
                       req_url=req_url, css=self.css, trim_style_tags=self.trim_style_tags)


class TitleSpider(Spider):
    """
    article title is in the first page and content in the second page
    """

    def __init__(self, start_urls, index_xpath, article_title_xpath, article_content_xpath, article_trim_xpaths=None,
                 index_limit_count=None, index_reverse=False, browser=False, css=None):
        super(TitleSpider, self).__init__(start_urls, index_xpath, article_title_xpath, article_content_xpath,
                                          article_trim_xpaths, index_limit_count, index_reverse, browser, css)

    def parse(self, response):
        content_urls = response.xpath(self.index_xpath).extract()
        titles = response.xpath(self.article_title_xpath).extract()

        if len(content_urls) != len(titles):
            self.logger.warning(f'Xpath maybe wrong {self.index_xpath}`{self.article_title_xpath}')

        if self.index_limit_count:
            content_urls = content_urls[:self.index_limit_count]
            titles = titles[:self.index_limit_count]

        if content_urls:
            for i in range(0, len(content_urls)):
                content_url = content_urls[i]
                title = titles[i]
                full_url = urllib.parse.urljoin(self.start_urls[0], content_url)

                if not is_crawled_url(full_url):
                    self.logger.info(f"Begin crawl`{full_url}")
                    yield response.follow(content_url, self.content_parse, meta={"title": title})
        else:
            self.logger.error("Site maybe has changed`%s", self.name)

    def content_parse(self, response):
        title = response.meta['title']

        try:
            content = response.xpath(self.article_content_xpath).extract_first()
        except AttributeError:
            self.logger.warning("Xpath Error`%s", response.url)
            return False

        url = response.url
        try:
            req_url = response.meta['redirect_urls'][0]
        except KeyError:
            req_url = url

        yield FeedItem(title=title, content=content, url=url, name=self.name, trims=self.article_trim_xpaths,
                       req_url=req_url, css=self.css)
