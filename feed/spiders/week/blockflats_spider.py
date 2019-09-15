
from feed.spiders.spider import Spider


class BlockflatsSpider(Spider):
    name = 'blockflats'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://blockflats.com/weekly',
                        ],
                        index_xpath="//div[@class='ignore-weeklys']/a/@href",
                        article_title_xpath="//div[@class='ignore-container']/h3/text()",
                        article_content_xpath="//div[@class='ignore-container']",
                        article_trim_xpaths=[
                            "//div[@class='ignore-container']/h3"
                        ],
                        index_limit_count=1,
                        css='.ignore-content-item{padding: 1rem 0;} .ignore-content-item-source{font-size:1.2rem;}',
                        )
