from feed.spiders.spider import Spider


class EzindieWeeklySpider(Spider):
    name = 'ezindie'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.ezindie.com/weekly',
                        ],
                        index_xpath='//div[@class="article-item"]/a/@href',
                        article_title_xpath="//article/div/h1/text()",
                        article_content_xpath='//article',
                        index_reverse=True,
                        article_trim_xpaths=[
                            "//article/div/h1",
                        ]
                        )
