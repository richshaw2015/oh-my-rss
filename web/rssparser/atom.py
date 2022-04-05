
import django
from django.urls import resolve
from web.models import *
from web.utils import generate_rss_avatar, get_with_retry, get_short_host_name, write_dat2_file, \
    get_html_text, trim_brief
import logging
import feedparser
import urllib
from bs4 import BeautifulSoup
from io import BytesIO
from django.conf import settings
from feed.utils import current_ts, mark_crawled_url, is_crawled_url, get_hash_name

logger = logging.getLogger(__name__)


def add_qnmlgb_feed(feed_url):
    """
    解析 qnmlgb.tech RSS 源
    :param feed_url:
    :return:
    """
    feed_obj = feedparser.parse(feed_url)

    title = feed_obj.feed.get('title')
    name = get_hash_name(settings.QNMLGB_HOST + title)

    site = Site.objects.filter(name=name)
    if site:
        logger.info(f"源已经存在：`{feed_url}")

        return {"site": site[0].pk}

    cname = title[:20]
    link = feed_obj.feed.link[:1024]
    brief = feed_obj.feed.subtitle[:200]
    favicon = feed_obj.feed.image.link.replace('/64.ico', '/96')

    try:
        site = Site(name=name, cname=cname, link=link, brief=brief, star=19, copyright=20,
                    creator='wemp', rss=feed_url, favicon=favicon)
        site.save()

        return {"site": site.pk}
    except:
        logger.error(f'处理源出现异常：`{feed_url}')

    return None


def add_atom_feed(feed_obj):
    """
    解析普通的 RSS 源
    :param feed_obj:
    :return: 解析结果，成功字典；失败 None
    """
    url = feed_obj.url

    if feed_obj.feed.get('title'):
        name = get_hash_name(url)

        site = Site.objects.filter(name=name, status='active')
        if site:
            logger.info(f"源已经存在：`{url}")

            return {"site": site[0].pk}

        cname = feed_obj.feed.title[:50]

        if feed_obj.feed.get('link'):
            link = feed_obj.feed.link[:1024]
        else:
            link = url

        if feed_obj.feed.get('subtitle'):
            brief = trim_brief(get_html_text(feed_obj.feed.subtitle))[:200]
        else:
            brief = feed_obj.feed.title

        author = feed_obj.feed.get('author') or get_short_host_name(link)

        # 使用默认头像
        favicon = generate_rss_avatar(link)

        try:
            site = Site(name=name, cname=cname, link=link, brief=brief, star=9, copyright=30,
                        creator='user', rss=url, favicon=favicon, author=author)
            site.save()

            return {"site": site.pk, "creator": "user"}
        except:
            logger.error(f'处理源出现异常：`{url}')

    else:
        logger.warning(f"RSS 解析失败：`{url}")

    return None


def atom_spider(site):
    """
    更新源内容
    """
    resp = get_with_retry(site.rss)

    if resp is None:
        if site.star > 9:
            logger.warning(f"RSS 源可能失效了`{site.rss}")
        else:
            logger.info(f"RSS源可能失效了`{site.rss}")
        return None

    content = BytesIO(resp.content)
    feed_obj = feedparser.parse(content)

    feed_obj.entries.reverse()
    for entry in feed_obj.entries:
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
            author = ''

        try:
            value = entry.content[0].value
        except (AttributeError, IndexError):
            value = None

        if not value:
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

        try:
            uindex = current_ts()

            article = Article(site=site, title=title, author=author, src_url=link, uindex=uindex)
            article.save()

            write_dat2_file(uindex, site.id, value)

            mark_crawled_url(link)
        except django.db.utils.IntegrityError:
            logger.info(f'数据重复插入：`{title}`{link}')
        except:
            logger.warning(f'数据插入异常：`{title}`{link}')

    return True


def add_self_feed(feed_url):
    """
    解析本站提供的 RSS 源
    :param feed_url:
    :return: 解析结果，成功字典；失败 None
    """

    feed_path = urllib.parse.urlparse(feed_url).path

    try:
        site_id = resolve(feed_path).kwargs.get('site_id')

        try:
            site = Site.objects.get(pk=site_id, status='active')
            return {"site": site.pk}
        except:
            logger.warning(f'订阅源不存在：`{feed_url}')
    except:
        pass

    return None
