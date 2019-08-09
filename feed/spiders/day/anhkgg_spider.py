
from feed.spiders.spider import Spider


class AnhkggSpider(Spider):
    name = 'anhkgg'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://anhkgg.com',
                        ],
                        index_xpath='//header/h1/a/@href',
                        article_title_xpath="//h1[@class='article-title']/text()",
                        article_content_xpath="//div[@class='article-entry']",
                        index_limit_count=3,
                        article_trim_xpaths=[
                            "//div[@class='page-reward']"
                        ]
                        )
