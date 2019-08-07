
from feed.spiders.spider import Spider


class TxdSpider(Spider):
    name = 'txd'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.yuque.com/txd-team/fe-report',
                        ],
                        index_xpath="//a[contains(text(),'第 ')]/@href",
                        article_title_xpath='//article//h1/text()',
                        article_content_xpath='//article',
                        article_trim_xpaths=[
                            '//h1'
                        ]
                        )
