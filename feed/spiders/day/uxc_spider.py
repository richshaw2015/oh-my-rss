
from feed.spiders.spider import Spider


class UxcSpider(Spider):
    name = 'uxc'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://ued.baidu.com/case',
                        ],
                        index_xpath="//ul[@class='case-article-list']/li/a/@href",
                        article_title_xpath="//div[@class='article-title']/text()",
                        article_content_xpath="//div[@class='article-content']",
                        index_limit_count=2,
                        )
