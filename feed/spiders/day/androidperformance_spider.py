
from feed.spiders.spider import Spider


class AndroidPerformanceSpider(Spider):
    name = 'androidperformance'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.androidperformance.com',
                        ],
                        index_xpath="//article/a/@href",
                        article_title_xpath="//*[@class='post-title']/a/text()",
                        article_content_xpath="//*[@class='article-entry']",
                        index_limit_count=3,
                        )
