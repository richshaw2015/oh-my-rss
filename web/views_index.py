from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse
from .models import *
from .utils import get_client_ip, add_refer_host, incr_redis_key, current_day
import urllib
import logging
import os
from user_agents import parse
from django.conf import settings

logger = logging.getLogger(__name__)


def index(request):
    """
    index home page
    :param request:
    :return:
    """
    logger.info("收到首页请求：`%s", get_client_ip(request))

    # PC 版、手机版适配
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

    if user_agent.is_pc:
        index_number = 8
    else:
        index_number = 10
    # render default article list
    articles = Article.objects.filter(status='active', site__star__gte=20).order_by('-id')[:index_number]

    referer = request.META.get('HTTP_REFERER', '')
    if referer:
        host = urllib.parse.urlparse(referer).netloc
        if host and host not in settings.ALLOWED_HOSTS:
            logger.info(f"收到外域来源：`{host}`{referer}")
            try:
                add_refer_host(host)
                incr_redis_key(settings.REDIS_REFER_PV_KEY % host)
                incr_redis_key(settings.REDIS_REFER_PV_DAY_KEY % (host, current_day()))
            except:
                logger.warning("外域请求统计异常")

    context = dict()
    context['articles'] = articles

    if user_agent.is_pc:
        return render(request, 'index.html', context)
    else:
        return render(request, 'mobile/index.html', context)


def article(request, uindex):
    """
    详情页，主要向移动端、搜索引擎提供
    """
    try:
        article = Article.objects.get(uindex=uindex)

        context = dict()
        context['article'] = article

        return render(request, 'mobile/article.html', context=context)
    except:
        logger.warning(f"获取文章详情请求处理异常：`{uindex}")

    return HttpResponseNotFound("Param error")


def robots(request):
    sitemap = os.path.join(request.build_absolute_uri(), '/sitemap.txt')
    return HttpResponse(f'''User-agent: *\nDisallow: /dash\n\nSitemap: {sitemap}''')


def sitemap(request):
    indexs = Article.objects.filter(status='active', site__star__gte=20).order_by('-id').\
        values_list('uindex', flat=True)[:500]

    url = request.build_absolute_uri('/')[:-1].strip("/")
    sites = [f'{url}/post/{i}' for i in indexs]

    return HttpResponse('\n'.join(sites))
