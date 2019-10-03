
from feed.spiders.spider import Spider


class BlockflatsSpider(Spider):
    name = 'blockflats'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://blockflats.com/weekly',
                        ],
                        index_xpath="//div[@class='ignore-weeklys']/a/@href",
                        article_title_xpath="//div[@class='ignore-container']//div[@class='ignore-title']//text()",
                        article_content_xpath="//div[@class='ignore-container']",
                        article_trim_xpaths=[
                            "//div[@class='ignore-container']//div[@class='ignore-title']"
                        ],
                        index_limit_count=2,
                        css='.ignore-content-item{padding: 1rem 0;} .ignore-content-item-source{font-size: 1.2rem;}'
                            '.ignore-content-item-title{font-weight: bold; color: rgb(233, 119, 43);}',
                        )
