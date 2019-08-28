
from feed.spiders.spider import Spider


class ColobuSpider(Spider):
    name = 'colobu'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://colobu.com/',
                        ],
                        index_xpath="//header/h1/a/@href",
                        article_title_xpath="//header/h1/text()",
                        article_content_xpath="//div[@class='article-entry']",
                        index_limit_count=3,
                        )
