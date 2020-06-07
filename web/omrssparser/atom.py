
import django
from django.urls import resolve
from web.models import *
from web.utils import get_hash_name, generate_rss_avatar, get_host_name, guard_log, set_updated_site
from web.omrssparser.wemp import parse_weixin_page
import logging
import feedparser
import requests
import urllib
from bs4 import BeautifulSoup
from io import BytesIO
from feed.utils import current_ts, mark_crawled_url, is_crawled_url
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError

logger = logging.getLogger(__name__)


def parse_atom(feed_url):
    """
    解析普通的 RSS 源
    :param feed_url:
    :return: 解析结果，成功字典；失败 None
    """
    feed_obj = feedparser.parse(feed_url)

    if feed_obj.feed.get('title'):
        name = get_hash_name(feed_url)
        cname = feed_obj.feed.title[:20]

        if feed_obj.feed.get('link'):
            link = feed_obj.feed.link[:1024]
        else:
            link = feed_url

        if feed_obj.feed.get('subtitle'):
            brief = feed_obj.feed.subtitle[:100]
        else:
            brief = cname

        author = feed_obj.feed.get('author', '')[:12]

        # 使用默认头像
        favicon = generate_rss_avatar(link)

        try:
            site = Site(name=name, cname=cname, link=link, brief=brief, star=9, freq='小时', copyright=30, tag='RSS',
                        creator='user', rss=feed_url, favicon=favicon, author=author)
            site.save()
        except django.db.utils.IntegrityError:
            logger.info(f"源已经存在：`{feed_url}")
        except:
            logger.error(f'处理源出现未知异常：`{feed_url}')

        return {"name": name}
    else:
        logger.warning(f"RSS解析失败：`{feed_url}")

    return None


def atom_spider(site):
    """
    更新源内容
    """
    try:
        resp = requests.get(site.rss, timeout=30, verify=False)
    except:
        if site.star > 9:
            guard_log(f"RSS 源可能失效了`{site.rss}")
        else:
            logger.info(f"RSS源可能失效了`{site.rss}")
        return None

    content = BytesIO(resp.content)
    feed_obj = feedparser.parse(content)

    for entry in feed_obj.entries[:12]:
        # 有些是空的
        if not entry:
            continue

        try:
            title = entry.title
            link = entry.link
        except AttributeError:
            logger.warning(f'必要属性获取失败：`{site.rss}')
            continue

        if is_crawled_url(link):
            continue

        try:
            author = entry['author'][:20]
        except:
            author = None

        try:
            value = entry.content[0].value
        except:
            value = entry.get('description') or entry.link

        # to absolute image url
        try:
            content_soup = BeautifulSoup(value, "html.parser")

            for img in content_soup.find_all('img'):
                rel_src = img.attrs.get('src')
                abs_src = urllib.parse.urljoin(link, rel_src)
                img.attrs['src'] = abs_src

            value = str(content_soup)
        except:
            logger.warning(f'修复图片路径异常：`{title}`{link}')

        # 公众号 RSS 二次抓取
        if get_host_name(site.rss) in ('qnmlgb.tech', ):
            if get_host_name(link) in ('mp.weixin.qq.com', ):
                try:
                    rsp = requests.get(link, timeout=10)
                    title, author, value = parse_weixin_page(rsp)
                except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
                    logger.warning(f"公众号二次爬取出现网络异常：`{link}")
                except:
                    logger.warning(f"公众号二次爬取出现未知异常：`{link}")

        try:
            article = Article(site=site, title=title, author=author, src_url=link, uindex=current_ts(), content=value)
            article.save()

            mark_crawled_url(link)
        except django.db.utils.IntegrityError:
            logger.info(f'数据重复插入：`{title}`{link}')
        except:
            logger.warning(f'数据插入异常：`{title}`{link}')

    set_updated_site(site.name)
    return True


def parse_self_atom(feed_url):
    """
    解析本站提供的 RSS 源
    :param feed_url:
    :return: 解析结果，成功字典；失败 None
    """

    feed_path = urllib.parse.urlparse(feed_url).path

    try:
        name = resolve(feed_path).kwargs.get('name')
    except:
        name = None

    if name:
        try:
            Site.objects.get(name=name, status='active')
            return {"name": name}
        except:
            logger.warning(f'订阅源不存在：`{feed_url}')

    return None
