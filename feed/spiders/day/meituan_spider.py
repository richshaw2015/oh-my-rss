
from feed.spiders.spider import Spider


class MeituanSpider(Spider):
    name = 'meituan'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://tech.meituan.com',
                        ],
                        index_xpath='//header/a/@href',
                        article_title_xpath='//*[@id="post_detail"]/article/header/h1/text()',
                        article_content_xpath='//*[@id="post_detail"]/article/div[@class="article__content"]',
                        index_limit_count=3,
                        )
