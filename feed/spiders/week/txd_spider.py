
from feed.spiders.spider import Spider


class TxdWeeklySpider(Spider):
    name = 'txd'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.yuque.com/txd-team/fe-report',
                        ],
                        index_xpath='//div[@class="main-book-cover-contents"]//span[@class="name"]//a/@href',
                        article_title_xpath="//h1/text()",
                        article_content_xpath="//div[@class='yuque-doc-content']",
                        index_limit_count=2,
                        browser=True
                        )
