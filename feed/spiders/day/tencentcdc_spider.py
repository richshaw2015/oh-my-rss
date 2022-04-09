
from feed.spiders.spider import Spider


class TencentCdcSpider(Spider):
    name = 'tencentcdc'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://cdc.tencent.com/percipience',
                        ],
                        index_xpath="//div[@class='container__wrapper--center']/div/div//a/@href",
                        article_title_xpath="//div[@class='article--title']/text()",
                        article_content_xpath="//div[@class='dangerously-html-box']",
                        )
