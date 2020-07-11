from django.http import JsonResponse
from web.utils import *
import logging
from web.models import *

logger = logging.getLogger(__name__)


def init(request):
    user = get_login_user(request)

    if user or settings.DEBUG:
        from web.tasks import load_articles_to_redis_cron

        load_articles_to_redis_cron()

        return JsonResponse({})


def install(request):
    """
    部署后操作
    """
    return JsonResponse({})
