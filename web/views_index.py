from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponse
from .models import *
from .utils import get_client_ip, log_refer_request
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
    log_refer_request(request)

    # PC 版、手机版适配
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

    if user_agent.is_pc:
        index_number = 8
    else:
        index_number = 10

    # TODO 判断是否登录用户

    # render default article list
    articles = Article.objects.filter(status='active', site__star__gte=20).order_by('-id')[:index_number]

    context = dict()
    context['articles'] = articles
    context['github_oauth_key'] = settings.GITHUB_OAUTH_KEY

    if user_agent.is_pc:
        return render(request, 'index.html', context)
    else:
        return render(request, 'mobile/index.html', context)


def article(request, id):
    """
    详情页，主要向移动端、搜索引擎提供
    """
    log_refer_request(request)

    try:
        article = Article.objects.get(uindex=id)
    except:
        try:
            article = Article.objects.get(pk=id)
        except:
            logger.warning(f"获取文章详情请求处理异常：`{id}")
            return redirect('index')
    context = dict()
    context['article'] = article

    return render(request, 'mobile/article.html', context=context)


def robots(request):
    sitemap = os.path.join(request.build_absolute_uri(), '/sitemap.txt')
    return HttpResponse(f'''User-agent: *\nDisallow: /dash\n\nSitemap: {sitemap}''')


def sitemap(request):
    indexs = Article.objects.filter(status='active', site__star__gte=10).order_by('-id').\
        values_list('uindex', flat=True)[:1000]

    url = request.build_absolute_uri('/')[:-1].strip("/")
    sites = [f'{url}/post/{i}' for i in indexs]

    return HttpResponse('\n'.join(sites))
