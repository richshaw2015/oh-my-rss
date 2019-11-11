
from feed.spiders.spider import Spider


class JdonSpider(Spider):
    name = 'jdon'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.jdon.com/approval',
                        ],
                        index_xpath="//h3[@class='vid-name']/a/@href",
                        article_title_xpath="//title/text()",
                        article_content_xpath="//div[@class='post_body_content']",
                        index_limit_count=6,
                        )
