
from feed.spiders.spider import Spider


class GityuanSpider(Spider):
    name = 'gityuan'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://gityuan.com',
                        ],
                        index_xpath="//div[@class='post-preview']/a/@href",
                        article_title_xpath='//h1/text()',
                        article_content_xpath="//div[contains(@class, 'post-container')]",
                        index_limit_count=6,
                        )
