
from feed.spiders.spider import Spider


class YouzanSpider(Spider):
    name = 'youzan'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://tech.youzan.com',
                        ],
                        index_xpath='//h2/a/@href',
                        article_title_xpath='//header//h1/text()',
                        article_content_xpath='//section[@class="post-content"]',
                        index_limit_count=3,
                        )
