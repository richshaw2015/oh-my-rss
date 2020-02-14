
from feed.spiders.spider import Spider


class AdleredSpider(Spider):
    name = 'adlered'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.stackoverflow.wiki/blog',
                        ],
                        index_xpath="//h2[@class='item__title']/a/@href",
                        article_title_xpath="//h2[@class='item__title']/text()",
                        article_content_xpath="//div[@class='wrapper']",
                        index_limit_count=3,
                        )
