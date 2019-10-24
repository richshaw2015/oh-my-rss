
from feed.spiders.spider import Spider


class PmcaffSpider(Spider):
    name = 'pmcaff'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://coffee.pmcaff.com/?type=2',
                        ],
                        index_xpath="//h2[@class='title']/a/@href",
                        article_title_xpath="//div[@class='head']//h2[@class='title']/text()",
                        article_content_xpath="//div[@id='articleContent']",
                        index_limit_count=2,
                        article_trim_xpaths=[
                            "//div[@class='mo-fold-ft']",
                        ],
                        browser=True,
                        )
