
from feed.spiders.spider import Spider


class OldPandaSpider(Spider):
    name = 'oldpanda'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://old-panda.com/',
                        ],
                        index_xpath="//h2[@class='entry-title']/a/@href",
                        article_title_xpath="//h1[@class='entry-title']/text()",
                        article_content_xpath="//div[@class='entry-content clearfix']",
                        index_limit_count=2,
                        article_trim_xpaths=[
                            "//div[@class='at-below-post addthis_tool']",
                            "//div[@class='jp-relatedposts']"
                        ]
                        )
