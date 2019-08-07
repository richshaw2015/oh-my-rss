
from feed.spiders.spider import Spider


class TencentCdcSpider(Spider):
    name = 'tencentcdc'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://cdc.tencent.com',
                        ],
                        index_xpath="//div[@class='item-title']//a/@href",
                        article_title_xpath="//div[@class='content-title']/h3/text()",
                        article_content_xpath='//div[@class="content-details"]',
                        article_trim_xpaths=[
                            "//div[@class='content-title']",
                            "//div[@class='content-prevnext']",
                        ],
                        index_limit_count=3,
                        )
