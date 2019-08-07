
from feed.spiders.spider import Spider


class AliyunfeWeeklySpider(Spider):
    name = 'aliyunfeweekly'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://github.com/aliyunfe/weekly',
                        ],
                        index_xpath="//a[contains(text(),'》第')]/@href",
                        article_title_xpath="//h2//*[@class='final-path']/text()",
                        article_content_xpath="//div[@id='readme']",
                        index_limit_count=3,
                        index_reverse=True
                        )
