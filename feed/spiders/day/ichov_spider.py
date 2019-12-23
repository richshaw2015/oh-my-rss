
from feed.spiders.spider import Spider


class IchovSpider(Spider):
    name = 'ichov'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://ichov.com/diary',
                            'https://ichov.com/photo',
                        ],
                        index_xpath="//div[@class='artTitle']/h2/a/@href",
                        article_title_xpath="//h1[@class='dtitle']/text()",
                        article_content_xpath="//div[@class='dcontent']",
                        index_limit_count=1,
                        )
