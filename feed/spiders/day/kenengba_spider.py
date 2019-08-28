
from feed.spiders.spider import Spider


class KenengbaSpider(Spider):
    name = 'kenengba'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://kenengba.com',
                        ],
                        index_xpath="//h1/a/@href",
                        article_title_xpath="//h1/text()",
                        article_content_xpath="//div[@id='wtr-content']",
                        index_limit_count=3,
                        )
