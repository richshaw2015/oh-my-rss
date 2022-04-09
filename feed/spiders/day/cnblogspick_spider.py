
from feed.spiders.spider import Spider


class CnblogsPickSpider(Spider):
    name = 'cnblogspick'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.cnblogs.com/pick/',
                        ],
                        index_xpath='//a[@class="post-item-title"]/@href',
                        article_title_xpath='//*[@id="cb_post_title_url"]/span/text()',
                        article_content_xpath='//*[@id="cnblogs_post_body"]',
                        )
