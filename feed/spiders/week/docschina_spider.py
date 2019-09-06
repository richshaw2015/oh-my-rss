
from feed.spiders.spider import Spider


class DocschinaSpider(Spider):
    name = 'docschina'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://weekly.docschina.org/javascript/',
                        ],
                        index_xpath="//ul[@class='sidebar-links']/li/a[@class='sidebar-link']/@href",
                        article_title_xpath="//div[@class='content']/h2[1]/text()",
                        article_content_xpath="//div[@class='content']",
                        index_limit_count=2,
                        article_trim_xpaths=[
                            "//div[@class='content']/h2[1]",
                            "//a[@aria-hidden='true']"
                        ]
                        )
