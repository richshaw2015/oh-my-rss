from web.models import *
import feedparser
from feed.utils import current_ts, mark_crawled_url, is_crawled_url
import logging
import django
import requests
from io import BytesIO
from datetime import datetime
from django.utils.timezone import timedelta
import urllib
from bs4 import BeautifulSoup
# import pysnooper

logger = logging.getLogger(__name__)


# @pysnooper.snoop()
def update_all_user_feed():
    """
    更新所有 site
    """
    logger.info('开始运行定时更新RSS任务')

    now = datetime.now()

    # 按照不同频率更新
    if now.hour % 2 == 0:
        feeds = Site.objects.filter(status='active', creator='user').order_by('-star')
    elif now.hour % 2 == 1:
        feeds = Site.objects.filter(status='active', creator='user', star__gte=9).order_by('-star')

    for site in feeds:
        try:
            resp = requests.get(site.rss, timeout=30, verify=False)
        except:
            if site.star >= 9:
                logger.warning(f"RSS源可能失效了`{site.rss}")
            else:
                logger.info(f"RSS源可能失效了`{site.rss}")
            continue

        content = BytesIO(resp.content)
        feed_obj = feedparser.parse(content)

        max_count = 10
        if site.star < 20:
            max_count = 50

        for entry in feed_obj.entries[:max_count]:
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

            try:
                article = Article(site=site, title=title, author=author, src_url=link, uindex=current_ts(),
                                  content=value)
                article.save()
                mark_crawled_url(link)
            except django.db.utils.IntegrityError:
                logger.info(f'数据重复插入：`{title}`{link}')
            except:
                logger.warning(f'数据插入异常：`{title}`{link}')
    logger.info('定时更新RSS任务运行结束')


def clean_history_data():
    """
    清除历史数据
    :return:
    """
    logger.info('开始清理历史数据')

    last1month = datetime.now() - timedelta(days=30)
    last3month = datetime.now() - timedelta(days=90)
    last1year = datetime.now() - timedelta(days=365)

    Article.objects.all().prefetch_related('site').filter(site__star__lt=10, ctime__lte=last1month).delete()
    Article.objects.all().prefetch_related('site').filter(site__star__lt=20, ctime__lte=last3month).delete()
    Article.objects.all().prefetch_related('site').filter(site__star__lt=30, ctime__lte=last1year).delete()

    logger.info('历史数据清理完毕')
