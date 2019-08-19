
from feed.spiders.spider import Spider


class Blog360Spider(Spider):
    name = 'blog360'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://blogs.360.cn',
                        ],
                        index_xpath="//h1[@class='title']/a/@href",
                        article_title_xpath="//article//h1[@class='title']/text()",
                        article_content_xpath="//article//div[@class='entry-content']",
                        index_limit_count=3,
                        article_trim_xpaths=[
                            "//div[@class='toc']"
                        ]
                        )
