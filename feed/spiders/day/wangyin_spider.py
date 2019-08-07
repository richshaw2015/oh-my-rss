
from feed.spiders.spider import Spider


class WangYinSpider(Spider):
    name = 'wangyin'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://www.yinwang.org',
                        ],
                        index_xpath="//ul[@class='list-group']/li/a/@href",
                        article_title_xpath='//h2/text()',
                        article_content_xpath="//div[@class='inner']",
                        index_limit_count=3,
                        )
