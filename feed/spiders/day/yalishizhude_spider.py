
from feed.spiders.spider import Spider


class YalishizhudeSpider(Spider):
    name = 'yalishizhude'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://yalishizhude.com/',
                        ],
                        index_xpath="//h1[@class='post-title']/a/@href",
                        article_title_xpath="//h1[@class='post-title']/text()",
                        article_content_xpath="//div[@class='post-body']",
                        index_limit_count=3,
                        )
