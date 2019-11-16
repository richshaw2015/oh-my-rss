
from feed.spiders.spider import Spider


class UfoerSpider(Spider):
    name = 'ufoer'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://www.ufoer.com/',
                        ],
                        index_xpath="//article//a[@class='title info_flow_news_title']/@href",
                        article_title_xpath="//h1[@class='single-post__title']/text()",
                        article_content_xpath="//section[@class='article']",
                        index_limit_count=2,
                        )
