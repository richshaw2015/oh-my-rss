
from feed.spiders.spider import Spider


class MoeloveSpider(Spider):
    name = 'moelove'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://moelove.info/',
                        ],
                        index_xpath="//h2[@class='post-title']/a/@href",
                        article_title_xpath="//h1[@class='post-title']/text()",
                        article_content_xpath="//div[@class='post-content']",
                        index_limit_count=3,
                        )
