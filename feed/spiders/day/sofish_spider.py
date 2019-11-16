
from feed.spiders.spider import Spider


class SofishSpider(Spider):
    name = 'sofish'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://sofi.sh/',
                        ],
                        index_xpath="//div[@class='block']/h2/a/@href",
                        article_title_xpath="//a[@title='page.attributes.title']/h1/text()",
                        article_content_xpath="//div[@itemprop='articleBody']",
                        index_limit_count=2,
                        )
