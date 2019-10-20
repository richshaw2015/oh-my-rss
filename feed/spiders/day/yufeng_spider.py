
from feed.spiders.spider import Spider


class YufengSpider(Spider):
    name = 'yufeng'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://blog.yufeng.info/',
                        ],
                        index_xpath="//div[@class='post']/h2/a/@href",
                        article_title_xpath="//div[@class='post']/h2/text()",
                        article_content_xpath="//div[@class='post']/div[@class='content']",
                        index_limit_count=3,
                        article_trim_xpaths=[
                            "//div[@class='sharedaddy sd-sharing-enabled']",
                            "//div[@class='yarpp-related']",
                        ]
                        )
