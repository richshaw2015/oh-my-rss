from django.http import JsonResponse
from web.utils import *
from feed.utils import mkdir
import logging
from web.models import *
import shutil
import feedparser

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
    sites = Site.objects.filter(brief__contains='RSS provided')
    for site in sites:
        site.brief = trim_brief(site.brief)
        site.save()

    sites = Site.objects.filter(brief__contains=' Made with love')
    for site in sites:
        site.brief = trim_brief(site.brief)
        site.save()

    return JsonResponse({})
