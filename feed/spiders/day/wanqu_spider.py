
from feed.spiders.spider import Spider


class WanquSpider(Spider):
    name = 'wanqu'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://wanqu.co/issues/',
                        ],
                        index_xpath="//div[@class='col-md-3']/a/@href",
                        article_title_xpath="//h1[@class='wq-header']/text()",
                        article_content_xpath='//div[@class="row"]/div[@class="col-lg-12"]',
                        index_limit_count=2,
                        article_trim_xpaths=[
                            "//h1[@class='wq-header']",
                            "//*[@id='post-views']",
                        ],
                        trim_style_tags=['div', ]
                        )
