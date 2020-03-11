
import django
from web.models import *
import logging
import requests
from scrapy.http import HtmlResponse
from web.utils import save_avatar, get_host_name
from feed.utils import current_ts, is_crawled_url, mark_crawled_url
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import urllib
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_wemp_ershicimi(url, update=False):
    """
    解析微信公众号，www.ershicimi.com
    :param url: 公众号主页地址
    :param update: 如果已经存在，是否更新
    :return: 解析结果，成功返回字典；失败 None
    """
    try:
        rsp = requests.get(url, timeout=10)
    except:
        logger.warning(f'请求出现异常：`{url}')
        return None

    if rsp.ok:
        response = HtmlResponse(url=url, body=rsp.text, encoding='utf8')

        qrcode = response.selector.xpath("//img[@class='qr-code']/@src").extract_first()

        if qrcode:
            name = urllib.parse.parse_qs(urllib.parse.urlparse(qrcode).query)['username'][0]

            if name:
                if not Site.objects.filter(name=name).exists():
                    # 新增站点
                    cname = response.selector.xpath("//li[@class='title']//span[@class='name']/text()").\
                        extract_first().strip()

                    avatar = response.selector.xpath("//img[@class='avatar']/@src").extract_first().strip()
                    favicon = save_avatar(avatar, name)

                    brief = response.selector.xpath(
                        "//div[@class='Profile-sideColumnItemValue']/text()").extract_first().strip()

                    if cname and avatar and brief:
                        try:
                            site = Site(name=name, cname=cname, link=qrcode, brief=brief, star=19, freq='日更',
                                        creator='wemp', copyright=20, tag='公众号', rss=url, favicon=favicon)
                            site.save()
                        except:
                            logger.warning(f'新增公众号失败：`{name}')
                else:
                    # 更新内容
                    if update:
                        try:
                            site = Site.objects.get(name=name)
                            links = response.selector.xpath("//*[@class='weui_media_title']/a/@href").extract()[:3]
                            for link in links:
                                link = urllib.parse.urljoin(url, link)
                                wemp_spider(link, site)
                        except:
                            logger.warning(f'更新公众号内容出现异常：`{name}')
                return {"name": name}
            else:
                logger.warning(f'微信公众号 id 解析失败：`{qrcode}')
        else:
            logger.warning(f'二维码链接解析失败：`{url}')

    return None


def wemp_spider(url, site):
    """
    抓取微信内容
    :param url:
    :param site:
    :return:
    """
    if is_crawled_url(url):
        return

    try:
        rsp = requests.get(url, timeout=10)

        if rsp.ok:
            try:
                if get_host_name(rsp.url) == 'mp.weixin.qq.com':
                    title, author, content = parse_weixin_page(rsp)
                elif 'ershicimi.com' in get_host_name(rsp.url):
                    title, author, content = parse_ershicimi_page(rsp)
                else:
                    logger.warning(f'公众号域名解析异常：`{rsp.url}')
                    return
            except:
                logger.warning(f'公众号内容解析异常：`{rsp.url}')
                return

            article = Article(title=title, author=author, site=site, uindex=current_ts(),
                              content=content, src_url=url)
            article.save()

            mark_crawled_url(url)
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        logger.warning(f'公众号爬取出现网络异常：`{url}')
    except:
        logger.warning(f'公众号爬取出现未知异常：`{url}')


def parse_weixin_page(rsp):
    """
    解析 https://mp.weixin.qq.com/s?__biz=MjM5OD...
    :param rsp:
    :return:
    """
    response = HtmlResponse(url=rsp.url, body=rsp.text, encoding='utf8')

    title = response.selector.xpath('//h2[@id="activity-name"]/text()').extract_first().strip()
    content = response.selector.xpath('//div[@id="js_content"]').extract_first().strip()

    try:
        author = response.selector.xpath('//span[@id="js_author_name"]/text()'). \
            extract_first().strip()
    except:
        author = response.selector.xpath('//a[@id="js_name"]/text()').extract_first().strip()

    if title and content:
        content_soup = BeautifulSoup(content, "html.parser")

        for img in content_soup.find_all('img'):
            if img.attrs.get('data-src'):
                img.attrs['src'] = img.attrs['data-src']

        return title, author, str(content_soup)


def parse_ershicimi_page(rsp):
    """
    解析 https://www.ershicimi.com/p/3e250905e46b0827af501c19c1c3f2ed
    :param rsp:
    :return:
    """
    response = HtmlResponse(url=rsp.url, body=rsp.text, encoding='utf8')

    title = response.selector.xpath('//h1[@class="article-title"]/text()').extract_first().strip()
    author = response.selector.xpath('//div[@class="article-sub"]//a/text()').extract_first().strip()

    try:
        content = response.selector.xpath('//div[@id="js_content"]').extract_first().strip()
    except:
        content = response.selector.xpath('//div[@class="abstract"]').extract_first().strip()


    return title, author, content
