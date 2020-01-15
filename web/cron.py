
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

    last1month = datetime.now() - timedelta(days=30)
    last3month = datetime.now() - timedelta(days=90)
    last1year = datetime.now() - timedelta(days=365)

    Article.objects.all().prefetch_related('site').filter(site__star__lt=10, ctime__lte=last1month).delete()
    Article.objects.all().prefetch_related('site').filter(site__star__lt=20, ctime__lte=last3month).delete()
    Article.objects.all().prefetch_related('site').filter(site__star__lt=30, ctime__lte=last1year).delete()

    logger.info('历史数据清理完毕')
