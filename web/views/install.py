from django.http import JsonResponse
from web.utils import *
import logging

logger = logging.getLogger(__name__)


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
    return JsonResponse({})


def debug(request):
    from web.tasks import archive_article_cron
    archive_article_cron()
    return JsonResponse({})
