
from feed.spiders.spider import TitleSpider


class SegmentfaultSpider(TitleSpider):
    name = 'segmentfault'

    def __init__(self):
        TitleSpider.__init__(self,
                        start_urls=[
                            'https://segmentfault.com/weekly',
                        ],
                        index_xpath='//ul[@class="dirlist"]/li/a/@href',
                        article_title_xpath='//ul[@class="dirlist"]/li/a/text()',
                        article_content_xpath='//div[@class="edm__main"]',
                        article_trim_xpaths=[
                            '//div[@class="edm__footer"]',
                            '//div[@class="edm__heading"]',
                        ],
                        index_limit_count=2,
                        )
