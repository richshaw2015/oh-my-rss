
from feed.spiders.spider import Spider


class TeddysunSpider(Spider):
    name = 'teddysun'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://teddysun.com',
                        ],
                        index_xpath="//header/h2/a/@href",
                        article_title_xpath="//h1/a/text()",
                        article_content_xpath="//*[@class='article-content']",
                        index_limit_count=3,
                        )
