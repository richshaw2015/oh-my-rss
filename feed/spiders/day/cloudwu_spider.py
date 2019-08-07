
from feed.spiders.spider import Spider


class CloudwuSpider(Spider):
    name = 'cloudwu'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://blog.codingnow.com',
                        ],
                        index_xpath="//*[@class='entry-more-link']/a/@href",
                        article_title_xpath="//h3[@class='entry-header']/text()",
                        article_content_xpath="//div[@class='entry']",
                        article_trim_xpaths=[
                            "//h3[@class='entry-header']"
                        ],
                        index_limit_count=3,
                        )
