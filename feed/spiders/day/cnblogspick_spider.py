
from feed.spiders.spider import Spider


class CnblogsPickSpider(Spider):
    name = 'cnblogspick'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.cnblogs.com/pick/',
                        ],
                        index_xpath='//*[@id="post_list"]/div/div/h3/a/@href',
                        article_title_xpath='//*[@id="cb_post_title_url"]/text()',
                        article_content_xpath='//*[@id="cnblogs_post_body"]',
                        index_limit_count=5,
                        )
