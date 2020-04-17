
from feed.spiders.spider import Spider


class ByvoidSpider(Spider):
    name = 'byvoid'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.byvoid.com/',
                        ],
                        index_xpath="//section[@class='entry-body entry-body-content']/header/h1/a/@href",
                        article_title_xpath="//header/h1/a/text()",
                        article_content_xpath="//section[@class='entry-body entry-body-content']",
                        article_trim_xpaths=[
                            "//header/h1/a",
                            "//section[@class='social-buttons']",
                            "//section[@class='related-post']",
                        ],
                        index_limit_count=3,
                        )
