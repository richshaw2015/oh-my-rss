
from feed.spiders.spider import Spider


class JdcSpider(Spider):
    name = 'jdc'

    def __init__(self):
        # TODO fix code style
        Spider.__init__(self,
                        start_urls=[
                            'https://jdc.jd.com',
                        ],
                        index_xpath='//h2/a/@href',
                        article_title_xpath='//h2/a/text()',
                        article_content_xpath='//div[@class="post"]',
                        index_limit_count=3,
                        article_trim_xpaths=[
                            '//div[@class="crayon-toolbar"]',
                            '//div[@class="crayon-info"]',
                            '//div[@class="crayon-plain-wrap"]',
                        ]
                        )
