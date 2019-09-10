
from feed.spiders.spider import Spider


class RaychaseSpider(Spider):
    name = 'raychase'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://www.raychase.net',
                        ],
                        index_xpath='//*[@class="entry-header"]/h2/a/@href',
                        article_title_xpath='//h1[@class="entry-title"]/text()',
                        article_content_xpath='//*[@class="entry-content"]',
                        index_limit_count=3,
                        article_trim_xpaths=[
                            '//div[@class="yarpp-related"]',
                            '//div[@class="open_social_box share_box"]',
                        ]
                        )
