
from feed.spiders.spider import Spider


class KernelTaobaoSpider(Spider):
    name = 'kerneltaobao'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://kernel.taobao.org',
                        ],
                        index_xpath="//div[@class='article-title']/a/@href",
                        article_title_xpath="//h1[@class='post-title']/text()",
                        article_content_xpath="//div[@class='post-content']",
                        index_limit_count=2,
                        )
