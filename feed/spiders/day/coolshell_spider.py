
from feed.spiders.spider import Spider


class CoolshellSpider(Spider):
    name = 'coolshell'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://coolshell.cn',
                        ],
                        index_xpath='//h2[@class="entry-title"]/a/@href',
                        article_title_xpath='//h1[@class="entry-title"]/text()',
                        article_content_xpath='//div[@class="entry-content"]'
                        )
