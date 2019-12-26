
from feed.spiders.spider import Spider


class CoolShellSpider(Spider):
    name = 'coolshell'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://coolshell.cn',
                        ],
                        index_xpath='//h2[@class="entry-title"]/a/@href',
                        article_title_xpath='//h1[@class="entry-title"]/text()',
                        article_content_xpath='//div[@class="entry-content"]',
                        article_trim_xpaths=[
                            "//*[@id='wp_rp_first']",
                            "//*[@class='post-ratings-loading']",
                            "//*[@class='post-ratings']",
                        ],
                        index_limit_count=3,
                        )
