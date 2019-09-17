from feed.spiders.spider import Spider


class DtfeWeeklySpider(Spider):
    name = 'dtfeweekly'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://github.com/dt-fe/weekly',
                        ],
                        index_xpath="//td[@class='content']//a[contains(text(),'.md') and not(contains(text(),'readme.md'))]/@href",
                        article_title_xpath="//h2//*[@class='final-path']/text()",
                        article_content_xpath='//article',
                        index_reverse=True,
                        )
