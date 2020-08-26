
import django
from web.models import *
from web.utils import generate_rss_avatar, set_updated_site, get_with_retry, get_short_host_name, write_dat2_file, \
    save_avatar, get_html_text
import logging
import feedparser
import urllib
from bs4 import BeautifulSoup
from io import BytesIO
from feed.utils import current_ts, mark_crawled_url, is_crawled_url, get_hash_name

logger = logging.getLogger(__name__)


def add_postcast_feed(feed_obj):
    """
    播客类型的 RSS 源
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

        try:
            link = feed_obj.feed.content_detail.base
        except AttributeError:
            if feed_obj.feed.get('link'):
                link = feed_obj.feed.link[:1024]
            else:
                link = url

        if feed_obj.feed.get('subtitle'):
            brief = get_html_text(feed_obj.feed.subtitle)[:200]
        else:
            brief = feed_obj.feed.title

        try:
            author = feed_obj.feed.author_detail.name
        except AttributeError:
            author = feed_obj.feed.get('author') or get_short_host_name(link)

        # 使用默认头像
        if feed_obj.feed.get('image'):
            favicon = save_avatar(feed_obj.feed.image.href, name)
        else:
            favicon = generate_rss_avatar(link)

        try:
            site = Site(name=name, cname=cname, link=link, brief=brief, star=10, copyright=30,
                        creator='podcast', rss=url, favicon=favicon, author=author)
            site.save()

            return {"site": site.pk}
        except:
            logger.error(f'新增播客异常：`{url}')
    else:
        logger.warning(f"播客解析失败：`{url}")

    return None


def podcast_spider(site):
    """
    更新源内容
    """
    resp = get_with_retry(site.rss)

    if resp is None:
        logger.info(f"RSS 源可能失效了`{site.rss}")
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
            author = ''

        audio, img = '', ''
        if entry.get('links'):
            for el in entry['links']:
                if 'audio/' in el.type:
                    # TODO 增加播放速率控制
                    audio = f'''<p></p><audio id="omrss-audio" src="{el.href}" type="{el.type}" controls></audio><p></p>'''
                    break
        if entry.get('image'):
            img = f'''<p></p><img src="{entry.image.href}">'''

        try:
            value = entry.content[0].value
        except:
            value = entry.get('description') or entry.link

        value = audio + value + img

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
            mark_crawled_url(link)
        except:
            logger.warning(f'数据插入异常：`{title}`{link}')

    set_updated_site(site.pk)
    return True
