from django.http import JsonResponse
from web.utils import *
import logging
from web.models import *

logger = logging.getLogger(__name__)

wemp_dict = {}


def load_db_data(request):
    """
    加载文章数据到内存，调试使用
    """
    user = get_login_user(request)

    if user or settings.DEBUG:
        from web.tasks import load_articles_to_redis_cron, load_active_sites_cron

        load_active_sites_cron()
        load_articles_to_redis_cron()

        return JsonResponse({})


def install(request):
    """
    部署后操作
    """
    from web.tasks import build_whoosh_index_cron
    build_whoosh_index_cron()
    return JsonResponse({})


def debug(request):
    for site in Site.objects.filter(status='active', creator='wemp', rss__contains='www.ershicimi.com'):
        if site.cname in wemp_dict.keys():
            logger.info(site.cname)

    return JsonResponse({})
