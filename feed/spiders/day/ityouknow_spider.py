
from feed.spiders.spider import Spider


class ItyouknowSpider(Spider):
    name = 'ityouknow'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://www.ityouknow.com/',
                        ],
                        index_xpath="//h2[@class='post-list-title']/a/@href",
                        article_title_xpath="//div[@id='jumbotron-meta-info']/h1/text()",
                        article_content_xpath="//div[@class='col-md-9 markdown-body']",
                        index_limit_count=3,
                        article_trim_xpaths=[
                            "//div[@class='comment']"
                        ]
                        )
