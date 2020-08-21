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
    # from web.rssparser.mpwx import make_mpwx_job
    # site = Site.objects.get(pk=2910)
    # make_mpwx_job(site, 14)

    sites = Site.objects.filter(status='active', creator='wemp', rss__contains='anyv.net', favicon__contains='emoji/')
    for site in sites:
        name = site.name + '.jpg'
        if os.path.exists(os.path.join(settings.BASE_DIR, 'assets', 'avatar', name)):
            site.favicon = f'/assets/avatar/{name}'
            site.save()

    return JsonResponse({})
