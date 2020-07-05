
from django.shortcuts import render, redirect
from django.http import HttpResponse
from web.models import *
from web.utils import add_referer_stats, get_login_user, get_user_subscribe_feeds, set_user_read_article, is_sensitive_content
import logging
import os
from user_agents import parse
from .verify import verify_request
from django.db.models import Q

logger = logging.getLogger(__name__)


def article(request, pid):
    """
    详情页，主要向移动端、搜索引擎提供，这个页面需要做风控
    """
    # 外链统计
    add_referer_stats(request.META.get('HTTP_REFERER', ''))

    try:
        article = Article.objects.get(uindex=pid, status='active')
    except:
        return redirect('index')

    user = get_login_user(request)
    if user:
        set_user_read_article(user.oauth_id, pid)

    # 判断是否命中敏感词
    if is_sensitive_content(pid, article.content):
        user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

        if user_agent.is_mobile or user_agent.is_bot:
            logger.warning(f'文章命中了敏感词，转到原文：`{article.title}`{pid}')
            return redirect(article.src_url)
        else:
            logger.warning(f'文章命中了敏感词，禁止访问：`{article.title}`{pid}')
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
    sites = [f'{url}/p/{index}' for index in indexs]

    return HttpResponse('\n'.join(sites))


@verify_request
def insite_search(request):
    """
    站内搜索 TODO 支持多个关键字
    """
    user = get_login_user(request)
    keyword = request.POST.get('keyword', '').strip()

    logger.warning(f"搜索关键字：`{keyword}")

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

    rel_sites = Site.objects.filter(status='active').filter(
        Q(cname__icontains=keyword) | Q(brief__icontains=keyword)).order_by('-star')[:50]

    rel_articles = Article.objects.filter(is_recent=True, status='active', site__star__gte=10).filter(
        Q(title__icontains=keyword) | Q(content__icontains=keyword)
    ).order_by('-id')[:50]

    context = dict()

    context['user'] = user
    context['user_sub_feeds'] = user_sub_feeds
    context['rel_sites'] = rel_sites
    context['rel_articles'] = rel_articles
    context['keyword'] = keyword

    return render(request, 'search.html', context=context)
