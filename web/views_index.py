from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponse
from .models import *
from .utils import log_refer_request, get_login_user, get_user_sub_feeds, set_user_read_article
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
    # 记录访问来源
    log_refer_request(request)

    # PC 版、手机版适配
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

    index_number = 10
    if user_agent.is_pc:
        index_number = 8

    # 判断是否登录用户
    user = get_login_user(request)

    # 默认的渲染列表，区分是否登录用户
    if user is None:
        articles = Article.objects.filter(status='active', site__star__gte=20).order_by('-id')[:index_number]
    else:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)
        if not user_sub_feeds:
            logger.warning(f'用户未订阅任何内容：`{user.oauth_id}')
        articles = Article.objects.filter(status='active', site__name__in=user_sub_feeds).order_by('-id')[:index_number]

    context = dict()
    context['articles'] = articles
    context['user'] = user
    context['github_oauth_key'] = settings.GITHUB_OAUTH_KEY

    if user_agent.is_pc:
        return render(request, 'index.html', context)
    else:
        return render(request, 'mobile/index.html', context)


def article(request, id):
    """
    详情页，主要向移动端、搜索引擎提供，这个页面需要做风控
    """
    log_refer_request(request)
    user = get_login_user(request)

    try:
        article = Article.objects.get(uindex=id, status='active')
    except:
        try:
            article = Article.objects.get(pk=id, status='active')
        except:
            logger.warning(f"获取文章详情请求处理异常：`{id}")
            return redirect('index')

    if user:
        set_user_read_article(user.oauth_id, id)

    # 判断是否命中敏感词
    is_sensitive = False
    for word in settings.SENSITIVE_WORDS:
        if word in article.content:
            is_sensitive = True
            break

    if is_sensitive:
        user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
        if user_agent.is_mobile or user_agent.is_bot:
            logger.warning(f'文章命中了敏感词，转到原文：`{article.title}`{id}')
            return redirect(article.src_url)
        else:
            logger.warning(f'文章命中了敏感词，禁止访问：`{article.title}`{id}')
            return redirect('index')

    context = dict()
    context['article'] = article
    context['user'] = user

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
