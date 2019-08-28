
from feed.spiders.spider import Spider


class WeiwuhuiSpider(Spider):
    name = 'weiwuhui'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://weiwuhui.com',
                        ],
                        index_xpath="//h2/a/@href",
                        article_title_xpath="//header/h1/text()",
                        article_content_xpath="//*[@class='entry-content']",
                        index_limit_count=3,
                        )
