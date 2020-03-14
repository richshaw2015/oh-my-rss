
from web.models import *
import logging
from datetime import datetime
from django.utils.timezone import timedelta
from web.omrssparser.atom import atom_spider
from web.omrssparser.wemp import parse_wemp_ershicimi
from web.utils import is_active_rss, set_similar_article, get_similar_article, cal_cosine_distance
import jieba
from web.stopwords import stopwords
from bs4 import BeautifulSoup
from collections import Counter
import json
# import pysnooper

logger = logging.getLogger(__name__)


# @pysnooper.snoop()
def update_all_user_feed():
    """
    更新普通订阅源
    """
    logger.info('开始运行定时更新 RSS 任务')

    now, feeds = datetime.now(), []

    # 按照不同频率更新
    if now.hour % 2 == 0:
        feeds = Site.objects.filter(status='active', creator='user').order_by('-star')
    elif now.hour % 2 == 1:
        feeds = Site.objects.filter(status='active', creator='user', star__gte=9).order_by('-star')

    for site in feeds:
        try:
            if not is_active_rss(site.name):
                if site.star < 9:
                    continue
            atom_spider(site)
        except:
            logger.warning(f'爬取站点出现异常：`{site.cname}')

    logger.info('定时更新 RSS 任务运行结束')


def update_all_wemp_feed():
    """
    更新公众号源
    """
    logger.info('开始更新公众号内容')

    # 按照不同频率更新
    feeds = Site.objects.filter(status='active', creator='wemp').order_by('-star')

    for site in feeds:
        try:
            parse_wemp_ershicimi(site.rss, update=True)
        except:
            logger.warning(f'爬取公众号出现异常：`{site.cname}')

    logger.info('更新公众号内容结束')


def clean_history_data():
    """
    清除历史数据
    :return:
    """
    logger.info('开始清理历史数据')

    lastweek = datetime.now() - timedelta(days=7)
    last3month = datetime.now() - timedelta(days=90)
    lastyear = datetime.now() - timedelta(days=365)

    # (, 10)，直接删除
    Article.objects.filter(site__star__lt=10, ctime__lte=lastweek).delete()

    # [10, 20)，创建时间超过 3 个月，内容置空
    Article.objects.filter(site__star__gte=10, site__star__lt=20, ctime__lte=last3month).update(content=' ')

    # [20, )，创建时间超过一年，内容置空
    Article.objects.filter(site__star__gte=20, ctime__lte=lastyear).update(content=' ')

    logger.info('历史数据清理完毕')


def update_article_tag():
    """
    设置最近一周的文章标识、统计词频
    :return:
    """
    # 设置最近一周文章标识
    lastweek = datetime.now() - timedelta(days=7)

    Article.objects.filter(is_recent=True, ctime__lte=lastweek).update(is_recent=False)

    # 统计词频
    articles = Article.objects.filter(is_recent=True, status='active', site__star__gte=10, tags='').order_by('-id')

    for article in articles:
        content_soup = BeautifulSoup(article.content, 'html.parser')
        content_text = content_soup.get_text() + 3 * article.title
        seg_list = jieba.cut(content_text)
        words_list = []

        for seg in seg_list:
            seg = seg.strip().lower()

            if len(seg) > 1 and seg not in stopwords:
                words_list.append(seg)

        tags_list = dict(Counter(words_list).most_common(10))

        if tags_list:
            logger.info(f'{article.uindex}`{tags_list}')

            article.tags = json.dumps(tags_list)
            article.save()


def cal_article_distance():
    """
    计算新增文章的相似度，用于推荐订阅
    :return:
    """
    logger.info(f'开始文章相似度计算')

    articles = Article.objects.filter(is_recent=True, status='active', site__star__gte=10).exclude(tags='').\
        order_by('-id')

    lastmonth = datetime.now() - timedelta(days=30)

    for article in articles:

        similar_dict = {}

        if not get_similar_article(article.uindex):
            compare_articles = Article.objects.filter(status='active', site__star__gte=10, ctime__gt=lastmonth).\
                exclude(tags='').values('uindex', 'tags')

            for compare in compare_articles:
                src_tags = json.loads(article.tags)
                dest_tags = json.loads(compare['tags'])
                distance = cal_cosine_distance(src_tags, dest_tags)

                if 0.1 < distance < 1:
                    similar_dict[compare['uindex']] = distance

            if similar_dict:
                sorted_similar_dict = dict(sorted(similar_dict.items(), key=lambda v: v[1], reverse=True)[:10])

                logger.info(f'{article.uindex}`{sorted_similar_dict}')

                set_similar_article(article.uindex, sorted_similar_dict)

    logger.info(f'文章相似度计算结束')
