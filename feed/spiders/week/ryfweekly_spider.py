
from feed.spiders.spider import Spider


class RyfWeeklySpider(Spider):
    name = 'ryfweekly'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://github.com/ruanyf/weekly',
                        ],
                        index_xpath="//a[contains(text(),'第 ')]/@href",
                        article_title_xpath='//article//h1/text()',
                        article_content_xpath='//article',
                        article_trim_xpaths=[
                            '//article//h1'
                        ],
                        index_limit_count=3,
                        )
