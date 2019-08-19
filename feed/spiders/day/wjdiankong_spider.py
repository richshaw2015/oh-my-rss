
from feed.spiders.spider import Spider


class WjdiankongSpider(Spider):
    name = 'wjdiankong'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'http://www.wjdiankong.cn',
                        ],
                        index_xpath="//header/h2/a/@href",
                        article_title_xpath='//header/h1/a/text()',
                        article_content_xpath="//div/article",
                        index_limit_count=3,
                        article_trim_xpaths=[
                            '//div[@class="article-social"]'
                        ]
                        )
