
from feed.spiders.spider import Spider


class YafeileeSpider(Spider):
    name = 'yafeilee'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://yafeilee.com/archives',
                        ],
                        index_xpath="//a[@class='blog-title']/@href",
                        article_title_xpath="//h2[@class='blog-title']/text()",
                        article_content_xpath="//div[@class='content markdown']",
                        index_limit_count=1,
                        )
