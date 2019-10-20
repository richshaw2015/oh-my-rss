
from feed.spiders.spider import Spider


class CssforestSpider(Spider):
    name = 'cssforest'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://blog.cssforest.org/',
                        ],
                        index_xpath="//section/h4/a/@href",
                        article_title_xpath="//article/header/h1/text()",
                        article_content_xpath="//main//article",
                        index_limit_count=2,
                        article_trim_xpaths=[
                            "//article/header",
                            "//article/footer",
                        ]
                        )
