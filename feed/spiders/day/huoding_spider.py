
from feed.spiders.spider import Spider


class HuodingSpider(Spider):
    name = 'huoding'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://blog.huoding.com/',
                        ],
                        index_xpath="//header/h1/a/@href",
                        article_title_xpath="//article/header/h1/text()",
                        article_content_xpath="//article//div[@class='entry-content']",
                        index_limit_count=2,
                        )
