from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from .models import *
from .utils import get_page_uv, get_subscribe_sites, get_login_user, get_user_sub_feeds, set_user_read_article
from .verify import verify_request
import logging
from datetime import datetime
from django.utils.timezone import timedelta

logger = logging.getLogger(__name__)


@verify_request
def get_article_detail(request):
    """
    获取文章详情；已登录用户记录已读
    """
    uindex = request.POST.get('id')
    user = get_login_user(request)
    mobile = request.POST.get('mobile', False)

    try:
        article = Article.objects.get(uindex=uindex, status='active')
    except:
        logger.warning(f"获取文章详情请求处理异常：`{uindex}")
        return HttpResponseNotFound("Param error")

    if user:
        set_user_read_article(user.oauth_id, uindex)

    context = dict()
    context['article'] = article

    if mobile:
        return render(request, 'mobile/article.html', context=context)
    else:
        return render(request, 'article/index.html', context=context)


@verify_request
def get_all_feeds(request):
    """
    获取订阅列表，已登录用户默认展示已订阅内容；游客展示推荐列表
    """
    user = get_login_user(request)
    if user is None:
        show_feeds = Site.objects.filter(status='active', star__gte=9).order_by('-star')
        hide_feeds = Site.objects.filter(status='active', star__lt=9).order_by('-star')
    else:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)
        show_feeds = Site.objects.filter(status='active', name__in=user_sub_feeds).order_by('-star')
        hide_feeds = Site.objects.filter(status='active').exclude(name__in=user_sub_feeds).order_by('-star')

    try:
        last_site = Site.objects.filter(status='active', creator='user', star__gte=9).order_by('-ctime')[0]
        submit_tip = f"「{last_site.cname[:20]}」({last_site.rss[:50]}) 最后被用户提交"
    except:
        submit_tip = '提交RSS源，例如：https://coolshell.cn/feed'

    context = dict()
    context['show_feeds'] = show_feeds
    context['hide_feeds'] = hide_feeds
    context['submit_tip'] = submit_tip
    context['user'] = user

    return render(request, 'feeds.html', context=context)


@verify_request
def get_homepage_intro(request):
    """
    获取首页介绍
    """
    mobile = request.POST.get('mobile', False)

    context = dict()
    context['mobile'] = mobile

    return render(request, 'intro.html', context=context)


@verify_request
def get_faq(request):
    """
    获取FAQ
    """
    mobile = request.POST.get('mobile', False)

    context = dict()
    context['mobile'] = mobile

    return render(request, 'faq.html', context=context)


@verify_request
def get_homepage_tips(request):
    """
    获取 tips
    """
    return render(request, 'tips.html')


@verify_request
def get_all_issues(request):
    """
    获取首页介绍
    """
    msgs = Message.objects.filter(status='active').order_by('-id')[:100]

    context = dict()
    context['msgs'] = msgs

    return render(request, 'issues.html', context=context)


@verify_request
def get_articles_list(request):
    """
    获取我的文章列表，游客展示默认推荐内容；登录用户展示其订阅内容
    """
    # 请求参数获取
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))
    mobile = request.POST.get('mobile', False)

    user = get_login_user(request)
    # 只查询最近一段时间的
    last2week = datetime.now() - timedelta(days=14)

    if user is None:
        visitor_sub_sites = get_subscribe_sites(tuple(sub_feeds), tuple(unsub_feeds))

        my_articles = Article.objects.all().prefetch_related('site').filter(
            status='active', site__name__in=visitor_sub_sites, ctime__gte=last2week).order_by('-id')[:300]
    else:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

        if not user_sub_feeds:
            logger.warning(f'用户未订阅任何内容：`{user.oauth_id}')

        my_articles = Article.objects.all().prefetch_related('site').filter(
            status='active', site__name__in=user_sub_feeds, ctime__gte=last2week).order_by('-id')[:999]

    if my_articles:
        # 分页处理，TODO 优化这里的性能
        paginator_obj = Paginator(my_articles, page_size)
        try:
            # 页面及数据
            pg = paginator_obj.page(page)
            num_pages = paginator_obj.num_pages
            uv = get_page_uv(pg)

            context = dict()
            context['pg'] = pg
            context['uv'] = uv
            context['num_pages'] = num_pages
            context['user'] = user

            if mobile:
                return render(request, 'mobile/list.html', context=context)
            else:
                return render(request, 'list.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseNotFound("Page number error")

    return HttpResponseNotFound("No Feeds subscribed")
