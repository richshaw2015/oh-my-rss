
from feed.spiders.spider import Spider


class JuejinSpider(Spider):
    name = 'juejin'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://juejin.im/?sort=monthly_hottest',
                        ],
                        index_xpath="//div[@class='entry-box']//a[@class='entry-link']/@href",
                        article_title_xpath="//h1[@class='article-title']/text()",
                        article_content_xpath="//div[@class='article-content']",
                        index_limit_count=6,
                        browser=True
                        )
