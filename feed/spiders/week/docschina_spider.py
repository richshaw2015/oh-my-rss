
from feed.spiders.spider import Spider


class DocschinaSpider(Spider):
    name = 'docschina'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://weekly.docschina.org/javascript/',
                        ],
                        index_xpath="//ul[@class='sidebar-links']/li/a[@class='sidebar-link']/@href",
                        article_title_xpath="//ul[@class='sidebar-links']/li/a[@class='sidebar-link']/text()",
                        article_content_xpath="//div[@class='content']",
                        article_trim_xpaths=[
                            "//div[@class='content']/h1",
                            "//a[@aria-hidden='true']"
                        ]
                        )
