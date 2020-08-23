from django.http import JsonResponse
from web.utils import *
from feed.utils import mkdir
import logging
from web.models import *
import shutil
import urllib

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
    # from web.rssparser.mpwx import make_mpwx_job
    # site = Site.objects.get(pk=2910)
    # make_mpwx_job(site, 14)
    import pickle

    R = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_FEED_DB,
                    decode_responses=True)
    CRAWL_PREFIX = 'CRAWL/*'
    for key in R.keys(CRAWL_PREFIX):
        R.delete(key)

    return JsonResponse({})
