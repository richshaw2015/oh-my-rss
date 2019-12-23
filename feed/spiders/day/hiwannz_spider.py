
from feed.spiders.spider import Spider


class HiwannzSpider(Spider):
    name = 'hiwannz'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://hiwannz.com/',
                        ],
                        index_xpath="//h2[@class='post-title']/a/@href",
                        article_title_xpath="//h1[@class='post-title']/text()",
                        article_content_xpath="//div[@class='post-content']",
                        index_limit_count=2,
                        )
