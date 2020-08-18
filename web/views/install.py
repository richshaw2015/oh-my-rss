from django.http import JsonResponse
from web.utils import *
import logging
from web.models import *

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
    from web.tasks import build_whoosh_index_cron
    build_whoosh_index_cron()
    return JsonResponse({})


def debug(request):
    from web.tasks import update_all_mpwx_cron, clear_expired_job_cron, cal_dvc_stat_cron
    cal_dvc_stat_cron()
    return JsonResponse({})
