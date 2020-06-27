from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from .models import *
from .utils import get_visitor_subscribe_feeds, get_login_user, get_user_subscribe_feeds, set_user_read_article, \
    get_similar_article, get_feed_ranking_dict, get_user_unread_count
from .verify import verify_request
import logging
from collections import defaultdict
import json
from .sql import *

logger = logging.getLogger(__name__)


@verify_request
def get_article_detail(request):
    """
    获取文章详情；已登录用户记录已读 TODO 服务器记录阅读数
    """
    uindex = request.POST.get('id')
    user = get_login_user(request)
    mobile = request.POST.get('mobile', False)

    try:
        article = Article.objects.get(uindex=uindex, status='active')
    except:
        logger.info(f"获取文章详情请求处理异常：`{uindex}")
        return HttpResponseNotFound("Param Error")

    if user:
        set_user_read_article(user.oauth_id, uindex)

    context = dict()
    context['article'] = article
    context['user'] = user

    if mobile:
        return render(request, 'mobile/article.html', context=context)
    else:
        return render(request, 'article/index.html', context=context)


@verify_request
def get_my_feeds(request):
    """
    获取我的订阅列表；游客已订阅、推荐订阅；登陆用户已订阅、推荐订阅
    """
    sub_feeds = json.loads(request.POST.get('sub_feeds') or '[]')
    unsub_feeds = json.loads(request.POST.get('unsub_feeds') or '[]')

    user = get_login_user(request)
    
    if user is None:
        visitor_sub_feeds = get_visitor_subscribe_feeds(tuple(sub_feeds), tuple(unsub_feeds))

        sub_sites = Site.objects.filter(status='active', pk__in=visitor_sub_feeds).order_by('-star')
        recom_sites = Site.objects.filter(status='active', star__gte=20).exclude(pk__in=visitor_sub_feeds).\
            order_by('-star')
    else:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id)

        sub_sites = Site.objects.filter(status='active', pk__in=user_sub_feeds).order_by('-star')
        recom_sites = Site.objects.filter(status='active', star__gte=20).exclude(pk__in=user_sub_feeds)\
            .order_by('-star')

    context = dict()
    context['sub_sites'] = sub_sites
    context['recom_sites'] = recom_sites
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
def get_recent_articles(request):
    """
    获取最近更新内容 TODO 优化查询性能，5 分钟更新一次？
    """
    user = get_login_user(request)
    recommend = request.POST.get('recommend', 'recommend')

    if recommend == 'unrecommend':
        articles = Article.objects.raw(get_other_articles_sql)
    elif recommend == 'recommend':
        articles = Article.objects.raw(get_recommend_articles_sql)
    else:
        logger.warning(f'未知的类型：{recommend}')
        return HttpResponseForbidden("Param Error")

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id)

    context = dict()
    context['articles'] = articles
    context['user'] = user
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'explore/recent_articles.html', context=context)


@verify_request
def get_explore(request):
    """
    获取发现页面
    """
    user = get_login_user(request)

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id)

    sites = Site.objects.filter(status='active').order_by('-id')[:50]

    context = dict()
    context['user'] = user
    context['sites'] = sites
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'explore/explore.html', context=context)


@verify_request
def get_recent_sites(request):
    """
    获取最近提交源
    """
    user = get_login_user(request)

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id)

    sites = Site.objects.filter(status='active').order_by('-id')[:50]

    context = dict()
    context['user'] = user
    context['sites'] = sites
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'explore/recent_sites.html', context=context)


@verify_request
def get_feed_ranking(request):
    """
    获取订阅源排行榜
    """
    user = get_login_user(request)

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id)

    feed_ranking = get_feed_ranking_dict()

    context = dict()
    context['user'] = user
    context['feed_ranking'] = feed_ranking
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'ranking/feed_ranking.html', context=context)


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
    user = get_login_user(request)

    msgs = Message.objects.filter(status='active').order_by('-id')[:20]

    context = dict()
    context['msgs'] = msgs
    context['user'] = user

    return render(request, 'issues.html', context=context)


@verify_request
def get_site_update_view(request):
    """
    获取更新的全局站点视图，游客 100 个，登陆用户 200 个站点
    """
    sub_feeds = json.loads(request.POST.get('sub_feeds') or '[]')
    unsub_feeds = json.loads(request.POST.get('unsub_feeds') or '[]')
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))

    user = get_login_user(request)

    if user is None:
        sub_update_feeds = get_visitor_subscribe_feeds(tuple(sub_feeds), tuple(unsub_feeds))
    else:
        sub_update_feeds = get_user_subscribe_feeds(user.oauth_id)

    sites = SiteUpdate.objects.filter(site_id__in=sub_update_feeds)

    if sites:
        # 分页处理
        paginator_obj = Paginator(sites, page_size)

        try:
            # 页面及数据
            pg = paginator_obj.page(page)
            num_pages = paginator_obj.num_pages

            # 计算未读数
            if user:
                for obj in pg.object_list:
                    obj.unread_count = get_user_unread_count(user.oauth_id, json.loads(obj.update_ids))

            context = dict()
            context['pg'] = pg
            context['num_pages'] = num_pages
            context['user'] = user

            return render(request, 'left/site_view.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseNotFound("Page Number Error")

    return HttpResponseNotFound("No Feeds Subscribed")


@verify_request
def get_article_update_view(request):
    """
    获取更新的文章列表视图；登录用户展示其订阅内容
    """
    # 请求参数获取
    sub_feeds = json.loads(request.POST.get('sub_feeds') or '[]')
    unsub_feeds = json.loads(request.POST.get('unsub_feeds') or '[]')
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))
    mobile = request.POST.get('mobile', False)

    user = get_login_user(request)

    if user is None:
        visitor_sub_feeds = get_visitor_subscribe_feeds(tuple(sub_feeds), tuple(unsub_feeds))

        my_articles = Article.objects.filter(status='active', is_recent=True,
                                             site_id__in=visitor_sub_feeds).order_by('-id')[:300]
    else:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id)

        my_articles = Article.objects.filter(
            status='active', is_recent=True, site_id__in=user_sub_feeds).order_by('-id')[:2000]

    if my_articles:
        # 分页处理
        paginator_obj = Paginator(my_articles, page_size)
        try:
            # 页面及数据
            pg = paginator_obj.page(page)
            num_pages = paginator_obj.num_pages

            context = dict()
            context['pg'] = pg
            context['num_pages'] = num_pages
            context['user'] = user

            if mobile:
                return render(request, 'mobile/list.html', context=context)
            else:
                return render(request, 'left/list_view.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseForbidden("Page Number Error")

    return HttpResponseForbidden("No Feeds Subscribed")


@verify_request
def get_site_article_update_view(request):
    """
    获取某个站点的更新文章列表视图
    """
    # 请求参数获取
    site_id = request.POST.get('site_id', 0)
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))

    user = get_login_user(request)

    site = Site.objects.get(pk=site_id, status='active')

    if user:
        site_articles = Article.objects.filter(site=site, status='active').order_by('-id')[:1000]
    else:
        site_articles = Article.objects.filter(site=site, status='active').order_by('-id')[:200]

    if site_articles:
        articles = [article.uindex for article in site_articles]

        # 分页处理
        paginator_obj = Paginator(site_articles, page_size)
        try:
            # 页面及数据
            pg = paginator_obj.page(page)
            num_pages = paginator_obj.num_pages

            context = dict()
            context['pg'] = pg
            context['num_pages'] = num_pages
            context['site'] = site
            context['user'] = user
            context['articles'] = articles

            return render(request, 'left/list2_view.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{site_id}")
            return HttpResponseForbidden("Page Number Error")

    return HttpResponseForbidden("No Sites Data")


@verify_request
def get_recommend_articles(request):
    """
    获取文章推荐的订阅源，只开放登录用户
    :param request:
    :return:
    """
    uindex = int(request.POST['id'])
    user = get_login_user(request)

    if uindex and user:
        recommend_articles = []
        relative_articles = list(get_similar_article(uindex).keys())
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id)

        for relative_uindex in relative_articles:
            try:
                article = Article.objects.get(uindex=relative_uindex, status='active')
            except:
                continue

            if article.site_id not in user_sub_feeds:
                recommend_articles.append(article)
            if len(recommend_articles) >= 3:
                break

        if recommend_articles:
            logger.info(f'推荐数据条数：`{len(recommend_articles)}`{user.oauth_name}')

            context = dict()
            context['recommend_articles'] = recommend_articles

            return render(request, 'recommend/relative_article.html', context=context)
        else:
            return JsonResponse({})

    return HttpResponseForbidden("No Recommend Data")
