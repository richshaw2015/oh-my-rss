
from feed.spiders.spider import Spider


class LuciferSpider(Spider):
    name = 'lucifer'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://lucifer.ren/blog/',
                        ],
                        index_xpath="//h2[@class='title']/a/@href",
                        article_title_xpath="//h1[@class='title']/a/text()",
                        article_content_xpath="//div[@class='article-entry']",
                        index_limit_count=3,
                        )
