
from feed.spiders.spider import Spider


class TtalkSpider(Spider):
    name = 'ttalk'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.ttalk.im/',
                        ],
                        index_xpath="//div[@class='text-left']/a/@href",
                        article_title_xpath="//h1/text()",
                        article_content_xpath="//div[contains(@class, 'content')]",
                        index_limit_count=3,
                        )
