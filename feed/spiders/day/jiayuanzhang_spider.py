
from feed.spiders.spider import Spider


class JiayuanzhangSpider(Spider):
    name = 'jiayuanzhang'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://blog.jiayuanzhang.com/',
                        ],
                        index_xpath="//h1[@class='post-title']/a/@href",
                        article_title_xpath="//div[@class='post']/h1/text()",
                        article_content_xpath="//div[@class='post']",
                        article_trim_xpaths=[
                            "//div[@class='post']/h1",
                        ]
                        )
