
from web.models import *
import logging
from datetime import datetime
from django.utils.timezone import timedelta
from web.omrssparser.atom import atom_spider
from web.omrssparser.wemp import parse_wemp_ershicimi
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
            parse_wemp_ershicimi(site.rss)
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
    last6month = datetime.now() - timedelta(days=180)
    lastyear = datetime.now() - timedelta(days=365)

    # (, 10)，直接删除
    Article.objects.all().prefetch_related('site').filter(site__star__lt=10, ctime__lte=lastweek).delete()

    # [10, 20)，创建时间超过半年，内容置空
    Article.objects.all().prefetch_related('site').filter(site__star__gte=10, site__star__lt=20,
                                                          ctime__lte=last6month).update(content=' ')

    # [20, )，创建时间超过一年，内容置空
    Article.objects.all().prefetch_related('site').filter(site__star__gte=20, ctime__lte=lastyear).update(content=' ')

    logger.info('历史数据清理完毕')


def set_is_recent_article():
    """
    设置最近一周的文章标识，每隔几分钟计算一次
    :return:
    """
    lastweek = datetime.now() - timedelta(days=7)

    logger.info('开始设置最近文章状态')

    Article.objects.filter(is_recent=True, ctime__lte=lastweek).update(is_recent=False)

    logger.info('设置最近文章状态结束')
