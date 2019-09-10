from feed.spiders.spider import Spider


class RyfWeeklySpider(Spider):
    name = 'golangweekly'

    def __init__(self):
        Spider.__init__(
            self,
            start_urls=['https://github.com/polaris1119/golangweekly'],
            index_xpath="//article//a[contains(text(),'第')]/@href",
            article_title_xpath='//article//h1/text()',
            article_content_xpath="//article",
            index_limit_count=3,
        )
