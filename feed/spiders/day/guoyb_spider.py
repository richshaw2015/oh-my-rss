
from feed.spiders.spider import Spider


class GuoybSpider(Spider):
    name = 'guoyb'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://blog.guoyb.com',
                        ],
                        index_xpath='//h1[@class="title"]/a/@href',
                        article_title_xpath='//h1[@class="title"]/text()',
                        article_content_xpath='//div[@class="entry"]',
                        index_limit_count=3,
                        )
