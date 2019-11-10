
from feed.spiders.spider import Spider


class FefWeeklySpider(Spider):
    name = 'fefweekly'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://github.com/richshaw2015/frontendfocus-cn',
                        ],
                        index_xpath="//a[contains(text(),'第 ')]/@href",
                        article_title_xpath='//article//h1/text()',
                        article_content_xpath='//article',
                        article_trim_xpaths=[
                            '//article//h1'
                        ],
                        index_limit_count=2,
                        )
