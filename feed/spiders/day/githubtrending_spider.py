
from feed.spiders.spider import Spider


class GithubTrendingSpider(Spider):
    name = 'githubtrending'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://github.com/trending?since=monthly',
                        ],
                        index_xpath='//*[@class="Box-row"]/h1/a/@href',
                        article_title_xpath='//meta[@property="og:title"]/@content',
                        article_content_xpath='//div[@id="readme"]',
                        index_limit_count=5,
                        )
