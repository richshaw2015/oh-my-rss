from feed.spiders.spider import Spider


class WangweiSpider(Spider):
    name = 'wangwei'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=['https://wangwei.one'],
                        index_xpath="//*[@id='posts']/article/div/link/@href",
                        article_title_xpath="//*[@id='posts']/article/div/header/h1/text()",
                        article_content_xpath="//*[@id='posts']/article/div/div[1]",
                        index_limit_count=3,
                        browser=True
                        )
    def start_requests(self):
        cookies = self.browser.get_cookies()
        print(cookies)