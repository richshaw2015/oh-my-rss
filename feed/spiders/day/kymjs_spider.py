
from feed.spiders.spider import Spider


class KymjsSpider(Spider):
    name = 'kymjs'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.kymjs.com',
                        ],
                        index_xpath="//div[@class='post-list-body']//a[@title]/@href",
                        article_title_xpath="//*[@id='myArticle']//header/h2/text()",
                        article_content_xpath="//*[@id='page']",
                        index_limit_count=3,
                        article_trim_xpaths=[
                            "//div[@class='only-phone']"
                        ]
                        )
