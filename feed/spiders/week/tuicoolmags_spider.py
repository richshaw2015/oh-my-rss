
from feed.spiders.spider import Spider


class TuicoolMagsSpider(Spider):
    name = 'tuicoolmags'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.tuicool.com/mags',
                            'https://www.tuicool.com/mags/tech',
                        ],
                        index_xpath='//div[@class="mag-period-item"]/a/@href',
                        article_title_xpath="//h3[@class='period-title']/text()[1]",
                        article_content_xpath='//div[@class="mag mag_detail"]',
                        article_trim_xpaths=[
                            "//h3[@class='period-title']"
                        ],
                        index_limit_count=2,
                        )
