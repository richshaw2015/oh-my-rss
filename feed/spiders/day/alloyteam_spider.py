
from feed.spiders.spider import Spider


class AlloyTeamSpider(Spider):
    name = 'alloyteam'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://www.alloyteam.com/page/0/',
                        ],
                        index_xpath="//ul[@class='articlemenu']/li/a[2]/@href",
                        article_title_xpath="//div[@class='title1']/a[2]/text()",
                        article_content_xpath="//div[@class='content_banner']",
                        index_limit_count=3,
                        )
