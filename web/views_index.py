from django.shortcuts import render
from .models import *
from .utils import get_client_ip, add_refer_host, incr_redis_key
import urllib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def index(request):
    """
    index home page
    :param request:
    :return:
    """
    logger.info("收到首页请求：`%s", get_client_ip(request))

    # render default article list
    articles = Article.objects.filter(status='active', site__star__gte=20).order_by('-id')[:10]

    referer = request.META.get('HTTP_REFERER', '')
    if referer:
        host = urllib.parse.urlparse(referer).netloc
        if host not in settings.ALLOWED_HOSTS:
            logger.warning(f"收到外域来源：`{host}`{referer}")
            try:
                add_refer_host(host)
                incr_redis_key(settings.REDIS_REFER_PV_KEY % host)
            except:
                logger.warning("外域请求统计异常")

    context = dict()
    context['articles'] = articles

    return render(request, 'index.html', context)


