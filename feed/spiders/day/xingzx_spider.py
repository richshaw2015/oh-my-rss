
from feed.spiders.spider import Spider


class XingzxSpider(Spider):
    name = 'xingzx'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://xingzx.org/',
                        ],
                        index_xpath="//h2[@class='post-title']/a/@href",
                        article_title_xpath="//div[@class='markdown-body editormd-preview-container']/h1/text()",
                        article_content_xpath="//div[@class='blog-body']",
                        )
