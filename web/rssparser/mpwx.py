
from web.models import *
import logging
from scrapy.http import HtmlResponse
from web.utils import save_avatar, get_with_retry, get_host_name, get_random_emoji, write_dat2_file
from feed.utils import current_ts, is_crawled_url, mark_crawled_url
import urllib
from bs4 import BeautifulSoup
import feedparser
import re

logger = logging.getLogger(__name__)


def make_mpwx_job(site, action):
    """
    从源地址生成远程任务
    """
    if action == 10:
        # RSS 直接解析
        feed_obj = feedparser.parse(site.rss)

        for entry in feed_obj.entries:
            # 有些是空的
            if not entry:
                continue

            if not is_crawled_url(entry.link):
                # 详情页爬虫，分布式执行
                job = Job(site=site, action=action + 10, url=entry.link, status=0)
                job.save()
    else:
        # 列表页爬虫，分布式执行
        job = Job(site=site, action=action, url=site.rss, status=0)
        job.save()

    return True


def parse_list_page(job):
    response, links = HtmlResponse(url=job.url, body=job.rsp, encoding='utf8'), []

    if job.action == 11:
        # ershicimi
        links = response.selector.xpath("//*[@class='weui_media_title']/a/@href").extract()
    elif job.action == 12:
        # wemp
        links = response.selector.xpath("//*[@class='post-item__main']//a[@class='post-item__title']/@href").extract()
    elif job.action == 13:
        # chansongme
        links = response.selector.xpath("//*[@class='feed_item_question']//a[@class='question_link']/@href").extract()
    elif job.action == 14:
        links = response.selector.xpath("//div[@class='grid news_desc']/h3/a/@href").extract()

    if not links:
        logger.warning(f"页面解析失败：`{job.url}")
        return 4

    for link in links:
        link = urllib.parse.urljoin(job.url, link)

        if is_crawled_url(link):
            continue

        new_job = Job(site=job.site, status=0, url=link, action=job.action + 10)
        new_job.save()

    return 2


def parse_detail_page(job):
    response = HtmlResponse(url=job.url, body=job.rsp, encoding='utf8')
    title, author, content = None, None, None

    # 判断跳转后的域名
    host = get_host_name(job.rsp_url)

    if job.action == 20 or 'mp.weixin.qq.com' in host:
        try:
            if response.selector.xpath("//div[@class='weui-msg__text-area']").extract_first():
                mark_crawled_url(job.url, job.rsp_url)
                logger.info(f"内容违规或删除：`{job.url}")
                return 6
        except:
            pass

        title, author, content = parse_mpwx_detail_page(response)

        if job.action != 20 and 'mp.weixin.qq.com' in host:
            logger.info(f"跳转到微信原文：`{job.url}`{job.rsp_url}`{title}")

    elif job.action == 21:
        title, author, content = parse_ershicimi_detail_page(response)
    elif job.action == 22:
        title, author, content = parse_wemp_detail_page(response)
    elif job.action == 23:
        title, author, content = parse_chuansongme_detail_page(response)
    elif job.action == 24:
        title, author, content = parse_anyv_detail_page(response)

    mark_crawled_url(job.url, job.rsp_url)

    if title is None:
        logger.warning(f"页面解析失败：`{title}`{job.url}")
        return 4
    else:
        try:
            uindex = current_ts()

            article = Article(title=title, author=author, site=job.site, uindex=uindex, content='',
                              src_url=job.url)
            article.save()

            write_dat2_file(uindex, job.site_id, content)
        except:
            logger.warning(f"插入文章异常：`{title}`{job.site}`{job.url}")
            return 7

        return 2


def parse_mpwx_detail_page(response):
    iframe = f'''<iframe frameborder=0 scrolling="no" seamless="seamless" src="{response.url}"></iframe>'''

    try:
        content = response.selector.xpath('//div[@id="js_content"]').extract_first().strip()
    except AttributeError:
        content = iframe

    try:
        title = response.selector.xpath('//h2[@id="activity-name"]/text()').extract_first().strip()
    except AttributeError:
        try:
            # 视频类的，只能加载出文字
            title = response.selector.xpath('//h2[@class="common_share_title js_video_channel_title"]/text()').\
                extract_first().strip()
            content += iframe
        except:
            # 无标题的、分享文章
            try:
                title = response.selector.xpath('//meta[@ property ="og:title"]/@content').extract_first().strip()[:30]
            except:
                title = ''

    try:
        author = response.selector.xpath('//span[@id="js_author_name"]/text()').extract_first().strip()
    except AttributeError:
        try:
            author = response.selector.xpath('//a[@id="js_name"]/text()').extract_first().strip()
        except AttributeError:
            author = ''

    if title and content:
        content_soup = BeautifulSoup(content, "html.parser")

        for img in content_soup.find_all('img'):
            if img.attrs.get('data-src'):
                img.attrs['src'] = img.attrs['data-src']

            if 'store.sogou.com' in img.attrs['src']:
                try:
                    img.attrs['src'] = img.attrs['src'].split('&url=')[1]
                except IndexError:
                    pass

        return title, author, str(content_soup)

    return None, None, None


def parse_ershicimi_detail_page(response):
    try:
        title = response.selector.xpath('//h1[@class="article-title"]/text()').extract_first().strip()
        author = response.selector.xpath('//div[@class="article-sub"]//a/text()').extract_first().strip()

        try:
            content = response.selector.xpath('//div[@id="js_content"]').extract_first().strip()
        except AttributeError:
            content = response.selector.xpath('//div[@class="abstract"]').extract_first().strip()

        if title and author and content:
            return title, author, content
    except:
        logger.warning(f"数据解析异常：`{response.url}")

    try:
        name = response.selector.xpath("//meta[@name='keywords']/@content").extract_first().split(',')[1]
        qrcode = response.selector.xpath("//img[@class='qr-code']/@src").extract_first()
        logger.info(f"二十次幂数据：`{qrcode}`{name}")
    except:
        pass

    return None, None, None


def parse_wemp_detail_page(response):
    try:
        title = response.selector.xpath('//h1[@class="post__title"]/text()').extract_first().strip()
        author = response.selector.xpath('//a[@class="post__author"]/span/text()').extract_first().strip()
        content = response.selector.xpath('//div[@id="content"]').extract_first().strip()

        if title and author and content:
            return title, author, content
    except:
        logger.warning(f"数据解析异常：`{response.url}")

    return None, None, None


def parse_chuansongme_detail_page(response):
    try:
        title = response.selector.xpath('//h2[@class="rich_media_title"]/text()').extract_first().strip()
        author = response.selector.xpath(
            "//*[@id='meta_content']/span[@class='rich_media_meta rich_media_meta_text']/text()").extract_first().strip()
        content = response.selector.xpath('//div[@id="js_content"]').extract_first().strip()

        if title and author and content:
            return title, author, content
    except:
        logger.warning(f"数据解析异常：`{response.url}")

    return None, None, None


def parse_anyv_detail_page(response):
    try:
        title = response.selector.xpath("//div[@class='product-details']/div[@class='desc span_3_of_2']//h1/text()")\
            .extract_first().strip()
        content = response.selector.xpath('//div[@id="js_content"]').extract_first().strip()

        if title and content:
            return title, '', content
    except:
        logger.warning(f"数据解析异常：`{response.url}")

    return None, None, None


def save_feed_to_db(name, cname, link, avatar, brief, url):
    site = Site.objects.filter(name=name)

    if site:
        logger.info(f"源已经存在：`{url}")
        return {"site": site[0].pk}
    else:
        # 新增站点
        if avatar:
            favicon = save_avatar(avatar, name, referer=url)
        else:
            favicon = get_random_emoji()

        try:
            site = Site(name=name, cname=cname, link=link, brief=brief, star=10, creator='wemp', copyright=20,
                        rss=url, favicon=favicon)
            site.save()

            return {"site": site.pk}
        except:
            logger.warning(f'新增公众号失败：`{name}')
    return None


def add_ershicimi_feed(url):
    """
    :return: 解析结果，成功返回字典；失败 None
    """
    rsp = get_with_retry(url)

    if rsp is None or not rsp.ok:
        return None

    response = HtmlResponse(url=url, body=rsp.text, encoding='utf8')

    qrcode = response.selector.xpath("//img[@class='qr-code']/@src").extract_first()
    cname = response.selector.xpath("//li[@class='title']//span[@class='name']/text()"). \
        extract_first().strip()
    avatar = response.selector.xpath("//img[@class='avatar']/@src").extract_first().strip()
    brief = response.selector.xpath("//div[@class='Profile-sideColumnItemValue']/text()").extract_first().strip()
    name = response.selector.xpath("//meta[@name='keywords']/@content").extract_first().split(',')[1]

    if qrcode and name and avatar and cname and brief:
        return save_feed_to_db(name, cname, qrcode, avatar, brief, url)
    else:
        logger.warning(f'字段解析异常：`{url}')

    return None


def add_wemp_feed(url):
    rsp = get_with_retry(url)

    if rsp is None or not rsp.ok:
        return None

    response = HtmlResponse(url=url, body=rsp.text, encoding='utf8')

    qrcode = response.selector.xpath("//*[@class='mp-info__main']/img[@class='mp-info__qr']/@src").extract_first()
    avatar = response.selector.xpath("//img[@class='post-item__avatar']/@src").extract_first().strip()
    brief = response.selector.xpath("//meta[@name='description']/@content").extract_first().strip()
    title = response.selector.xpath("//*[@class='mp-header']/h1/text()").extract_first().strip()

    cname, name = None, None
    try:
        cname, name = re.search(r'^.+? (.+?)\((.+?)\) .+$', title).groups()
    except:
        logger.warning(f"标题解析失败：`{title}")

    if qrcode and name and avatar and cname and brief:
        return save_feed_to_db(name, cname, qrcode, avatar, brief, url)
    else:
        logger.warning(f'字段解析异常：`{url}')

    return None


def add_chuansongme_feed(url):
    rsp = get_with_retry(url)

    if rsp is None or not rsp.ok:
        return None

    response = HtmlResponse(url=url, body=rsp.text, encoding='utf8')

    qrcode = response.selector.xpath("//img[@width='260px']/@src").extract_first()
    avatar = response.selector.xpath("//img[@class='profile_photo_img']/@src").extract_first().strip()
    brief = response.selector.xpath("//*[@class='inline_editor_value']/div[@class='inline']/span/text()").\
        extract_first().strip()
    keywords = response.selector.xpath("//meta[@name='keywords']/@content").extract_first()

    cname, name = None, None
    try:
        cname, name = keywords.split(',')[:2]
    except:
        logger.warning(f"标题解析失败：`{keywords}")

    if qrcode and name and avatar and cname and brief:
        return save_feed_to_db(name, cname, qrcode, avatar, brief, url)
    else:
        logger.warning(f'字段解析异常：`{url}')

    return None


def add_anyv_feed(url):
    rsp = get_with_retry(url)

    if rsp is None or not rsp.ok:
        return None

    response = HtmlResponse(url=url, body=rsp.text, encoding='utf8')

    # 没有二维码和头像
    avatar, link = '', url
    brief = response.selector.xpath("//*[@class='user_group']/li[2]/text()"
                                    ).extract_first().strip().split(':', 1)[1].split(', 微信搜索')[0]
    cname = response.selector.xpath("//div[@class='subtitle']/h1/a/text()").extract_first().strip()[:-4]
    name = response.selector.xpath("//*[@class='user_group']/li/a/text()").extract_first().strip().split(':')[-1]

    if not brief:
        brief = cname

    if name and cname and brief:
        return save_feed_to_db(name, cname, link, avatar, brief, url)
    else:
        logger.warning(f'字段解析异常：`{url}')

    return None
