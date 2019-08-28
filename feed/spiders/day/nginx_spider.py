
from feed.spiders.spider import Spider


class NginxSpider(Spider):
    name = 'nginx'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://www.nginx.cn',
                        ],
                        index_xpath="//div[@class='post']/h2/a/@href",
                        article_title_xpath="//div[@class='post']/h1/text()",
                        article_content_xpath="//div[@class='post']/div[@class='content']",
                        index_limit_count=3,
                        )
