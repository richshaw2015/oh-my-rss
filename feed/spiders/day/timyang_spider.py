
from feed.spiders.spider import Spider


class TimyangSpider(Spider):
    name = 'timyang'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://timyang.net',
                        ],
                        index_xpath="//h2/a/@href",
                        article_title_xpath="//*[@class='posttitle']/a/text()",
                        article_content_xpath="//*[@class='entry']",
                        index_limit_count=3,
                        )
