
from feed.spiders.spider import Spider


class MiniaspSpider(Spider):
    name = 'miniasp'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://blog.miniasp.com/',
                        ],
                        index_xpath="//h2[@class='post-title']/a/@href",
                        article_title_xpath="//h2[@class='post-title']/a/text()",
                        article_content_xpath="//section[@class='post-body text']",
                        index_limit_count=2,
                        )
