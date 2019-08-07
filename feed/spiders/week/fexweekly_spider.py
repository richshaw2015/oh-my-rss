
from feed.spiders.spider import Spider


class FexweeklySpider(Spider):
    name = 'fexweekly'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://fex.baidu.com/weekly/',
                        ],
                        index_xpath="//ul[@class='post-list']//a/@href",
                        article_title_xpath="//h1[@class='title']/text()",
                        article_content_xpath="//div[@class='content']",
                        index_limit_count=3,
                        )
