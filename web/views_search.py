from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .utils import log_refer_request, get_login_user, get_user_sub_feeds, set_user_read_article
import logging
import os
from user_agents import parse
from django.conf import settings
from .verify import verify_request
from django.db.models import Q

logger = logging.getLogger(__name__)


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
            # 仅用于短链分享
            article = Article.objects.get(pk=id, status='active')
        except:
            return redirect('index')

    # 历史的文章
    if not article.content.strip():
        return redirect(article.src_url)

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


@verify_request
def insite_search(request):
    """
    站内搜索
    """
    user = get_login_user(request)
    keyword = request.POST.get('keyword', '').strip()

    logger.warning(f"搜索关键字：`{keyword}")

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

    rel_sites = Site.objects.filter(status='active').filter(
        Q(cname__icontains=keyword) | Q(link__icontains=keyword) | Q(brief__icontains=keyword) |
        Q(rss__icontains=keyword)).order_by('-star')[:50]

    rel_articles = Article.objects.filter(is_recent=True, status='active', site__star__gte=10).filter(
        Q(title__icontains=keyword) | Q(src_url__icontains=keyword) | Q(content__icontains=keyword)
    ).order_by('-id')[:50]

    context = dict()

    context['user'] = user
    context['user_sub_feeds'] = user_sub_feeds
    context['rel_sites'] = rel_sites
    context['rel_articles'] = rel_articles
    context['keyword'] = keyword

    return render(request, 'search.html', context=context)
