import shutil

from django.http import JsonResponse
from web.utils import *
from web.models import Article, Site
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
    for s in range(1, 4843):
        if not Site.objects.filter(pk=s).exists():
            Article.objects.filter(site_id=s).delete()

            site_data = os.path.join(settings.HTML_DATA2_DIR, str(s))
            try:
                shutil.rmtree(site_data)
            except Exception as e:
                logger.info(e)

    return JsonResponse({})
