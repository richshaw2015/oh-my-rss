
from feed.spiders.spider import Spider


class HelloGithubSpider(Spider):
    name = 'hellogithub'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://github.com/521xueweihan/HelloGitHub/blob/master/README.md',
                        ],
                        index_xpath="//a[contains(text(),'第 ')]/@href",
                        article_title_xpath='//article//h1/text()',
                        article_content_xpath='//article',
                        article_trim_xpaths=[
                            '//h1'
                        ],
                        index_limit_count=3,
                        )
