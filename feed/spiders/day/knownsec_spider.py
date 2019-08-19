
from feed.spiders.spider import Spider


class KnownsecSpider(Spider):
    name = 'knownsec'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://blog.knownsec.com',
                        ],
                        index_xpath='//h2/a/@href',
                        article_title_xpath='//h1/text()',
                        article_content_xpath='//*[@id="post_content"]',
                        index_limit_count=3,
                        article_trim_xpaths=[
                            '//div[@class="crayon-toolbar"]',
                            '//div[@class="crayon-info"]',
                            '//div[@class="crayon-plain-wrap"]',
                        ]
                        )
