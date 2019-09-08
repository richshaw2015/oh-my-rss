
from feed.spiders.spider import Spider


class ZhangxinxuSpider(Spider):
    name = 'zhangxinxu'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.zhangxinxu.com/wordpress/',
                        ],
                        index_xpath='//h2/a/@href',
                        article_title_xpath='//div[@id="content"]//h2/text()',
                        article_content_xpath='//div[@class="entry"]//article',
                        index_limit_count=3,
                        article_trim_xpaths=[
                            "//article/p[@class='link']",
                            "//div[@class='similarity']",
                        ]
                        )
