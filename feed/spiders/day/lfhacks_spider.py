
from feed.spiders.spider import Spider


class LfhacksSpider(Spider):
    name = 'lfhacks'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.lfhacks.com/',
                        ],
                        index_xpath="//li[@class='article']/h4/a/@href",
                        article_title_xpath="//article[@class='article']/h1/text()",
                        article_content_xpath="//div[@itemprop='articleBody']",
                        index_limit_count=2,
                        )
