
from feed.spiders.spider import Spider


class ZcfySpider(Spider):
    name = 'zcfy'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://zcfy.cc',
                        ],
                        index_xpath='//div[@id="main_list"]//div[@class="uk-width-expand"]/a/@href',
                        article_title_xpath='//h2[@class="detail-title uk-margin-medium-top"]/text()',
                        article_content_xpath='//div[@class="uk-card-body uk-padding-remove-top"]',
                        index_limit_count=2,
                        article_trim_xpaths=[
                            '//div[@class="uk-padding uk-padding-remove-horizontal"]',
                            '//h2[@class="detail-title uk-margin-medium-top"]',
                        ]
                        )
