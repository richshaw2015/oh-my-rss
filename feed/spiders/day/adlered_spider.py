
from feed.spiders.spider import Spider


class AdleredSpider(Spider):
    name = 'adlered'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.stackoverflow.wiki/blog',
                        ],
                        index_xpath="//a[@class='article-title']/@href",
                        article_title_xpath="//h2[@class='article__title']/text()",
                        article_content_xpath="//section[@id='article-container']",
                        )
