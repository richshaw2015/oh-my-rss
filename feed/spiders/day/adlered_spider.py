
from feed.spiders.spider import Spider


class AdleredSpider(Spider):
    name = 'adlered'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.stackoverflow.wiki/blog',
                        ],
                        index_xpath="//h1/a/@href",
                        article_title_xpath="//h1[contains(@class, 'title')]/text()",
                        article_content_xpath="//div[@id='post-article']",
                        )
