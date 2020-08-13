
from feed.spiders.spider import Spider


class FrontendWeeklySpider(Spider):
    name = 'frontendweekly'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://frontend-weekly.com/',
                        ],
                        index_xpath="//ul[@class='articles']//li/a/@href",
                        article_title_xpath='//div[@class="search-noresults"]//h1/text()',
                        article_content_xpath='//div[@class="search-noresults"]',
                        article_trim_xpaths=[
                            '//div[@class="search-noresults"]//h1'
                        ],
                        )
