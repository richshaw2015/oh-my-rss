
from feed.spiders.spider import Spider


class JimmysongSpider(Spider):
    name = 'jimmysong'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://jimmysong.io/',
                        ],
                        index_xpath="//article[@class='post-preview']/a/@href",
                        article_title_xpath="//div[@class='post-heading']/h1/text()",
                        article_content_xpath="//article[@id='content']",
                        index_limit_count=3,
                        article_trim_xpaths=[
                            "//div[@class='entry-shang text-center']",
                        ]
                        )
