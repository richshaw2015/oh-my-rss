
from feed.spiders.spider import Spider


class FeihuSpider(Spider):
    name = 'feihu'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://feihu.me/blog/',
                        ],
                        index_xpath="//h2/a/@href",
                        article_title_xpath="//h1/text()",
                        article_content_xpath="//section",
                        index_limit_count=3,
                        article_trim_xpaths=[
                            "//h1[@class='post-title']",
                            "//p[@class='post-meta']",
                            "//div[@id='disqus_thread']",
                        ]
                        )
