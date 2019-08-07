
from feed.spiders.spider import Spider


class DevtangSpider(Spider):
    name = 'devtang'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://blog.devtang.com',
                        ],
                        index_xpath='//*[@id="main"]/section/a/@href',
                        article_title_xpath='//*[@id="main"]/article/header/h1/a/text()',
                        article_content_xpath='//*[@id="main"]/article/div',
                        index_limit_count=3,
                        )
