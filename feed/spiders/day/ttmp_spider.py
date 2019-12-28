from feed.spiders.spider import WeixinSpider


class TtmpSpider(WeixinSpider):
    name = 'ttmp'

    def __init__(self):
        WeixinSpider.__init__(self,
                        start_urls=[
                            'https://www.toutiao.io/posts/hot/7',
                        ],
                        index_xpath='//div[@class="meta" and contains(text(), "mp.weixin.qq.com")]/../h3/a/@href',
                        index_limit_count=20,
                        )
