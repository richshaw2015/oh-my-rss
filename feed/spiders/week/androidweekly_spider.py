
from feed.spiders.spider import Spider


class AndroidWeeklySpider(Spider):
    name = 'androidweekly'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://androidweekly.io',
                        ],
                        index_xpath="//article//h2/a/@href",
                        article_title_xpath='//h1/text()',
                        article_content_xpath="//div[@class='content']",
                        index_limit_count=3,
                        )
