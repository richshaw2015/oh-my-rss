
from feed.spiders.spider import Spider


class Coder4Spider(Spider):
    name = 'coder4'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.coder4.com/',
                        ],
                        index_xpath="//h1[@class='entry-title']/a/@href",
                        article_title_xpath="//h1[@class='entry-title']/text()",
                        article_content_xpath="//div[@class='entry-content']",
                        index_limit_count=2,
                        )
