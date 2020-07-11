from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from django.conf import settings
from web.models import *
from web.utils import get_visitor_subscribe_feeds, get_login_user, get_user_subscribe_feeds, set_user_read_article, \
    get_similar_article, get_feed_ranking_dict, get_user_unread_count, get_recent_site_articles, \
    get_site_last_id, get_user_unread_articles, get_user_unread_sites, get_user_ranking_list, get_sites_lastids
from web.verify import verify_request
import logging
import json

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

    user, reach_sub_limit = get_login_user(request), [False, 0]
    
    if user is None:
        visitor_sub_feeds = get_visitor_subscribe_feeds(tuple(sub_feeds), tuple(unsub_feeds))

        sub_sites = Site.objects.filter(status='active', pk__in=visitor_sub_feeds).order_by('-star')
        recom_sites = Site.objects.filter(status='active', star__gte=20).exclude(pk__in=visitor_sub_feeds).\
            order_by('-star')

        if len(visitor_sub_feeds) == settings.VISITOR_SUBS_LIMIT:
            reach_sub_limit = [True, settings.VISITOR_SUBS_LIMIT]
    else:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

        sub_sites = Site.objects.filter(status='active', pk__in=user_sub_feeds).order_by('-star')
        recom_sites = Site.objects.filter(status='active', star__gte=20).exclude(pk__in=user_sub_feeds)\
            .order_by('-star')

        if user.level < 10:
            if len(user_sub_feeds) == settings.USER_SUBS_LIMIT:
                reach_sub_limit = [True, settings.USER_SUBS_LIMIT]

    context = dict()
    context['sub_sites'] = sub_sites
    context['recom_sites'] = recom_sites
    context['user'] = user
    context['reach_sub_limit'] = reach_sub_limit

    return render(request, 'myfeeds.html', context=context)


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
    获取最近更新内容 TODO 优化查询性能
    """
    user = get_login_user(request)
    ids = get_sites_lastids()

    articles = Article.objects.filter(uindex__in=ids)

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

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
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

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
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

    sites = Site.objects.filter(status='active').order_by('-id')[:50]

    context = dict()
    context['user'] = user
    context['sites'] = sites
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'explore/recent_sites.html', context=context)


@verify_request
def get_ranking(request):
    """
    获取订阅源排行榜
    """
    user = get_login_user(request)

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

    feed_ranking = get_feed_ranking_dict()

    context = dict()
    context['user'] = user
    context['feed_ranking'] = feed_ranking
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'ranking/ranking.html', context=context)


@verify_request
def get_feed_ranking(request):
    """
    获取订阅源排行榜
    """
    user = get_login_user(request)

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

    feed_ranking = get_feed_ranking_dict()

    context = dict()
    context['user'] = user
    context['feed_ranking'] = feed_ranking
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'ranking/feed_ranking.html', context=context)


@verify_request
def get_user_ranking(request):
    user_ranking = get_user_ranking_list()

    context = dict()
    context['user_ranking'] = user_ranking

    return render(request, 'ranking/user_ranking.html', context=context)


@verify_request
def get_faq(request):
    """
    获取FAQ
    """
    mobile = request.POST.get('mobile', False)
    user = get_login_user(request)

    context = dict()
    context['mobile'] = mobile
    context['user'] = user

    return render(request, 'faq.html', context=context)


@verify_request
def get_donate_guide(request):
    return render(request, 'donate.html')


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
    onlyunread = request.POST.get('onlyunread', 'no') == 'yes'

    user = get_login_user(request)

    if user is None:
        my_feeds = get_visitor_subscribe_feeds(tuple(sub_feeds), tuple(unsub_feeds))
    else:
        my_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

    # 过滤有内容更新的
    if user and onlyunread:
        my_feeds = get_user_unread_sites(user.oauth_id, my_feeds)

    my_feeds = sorted(my_feeds, key=lambda t: get_site_last_id(t), reverse=True)

    if my_feeds:
        # 分页处理
        try:
            paginator_obj = Paginator(my_feeds, page_size)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseNotFound("Page Number Error")

        pg = paginator_obj.page(page)
        num_pages = paginator_obj.num_pages
        sites = Site.objects.filter(pk__in=pg.object_list, status='active').order_by('-star')[:50]

        for site in sites:
            recent_articles = get_recent_site_articles(site.pk)

            site.update_count = len(recent_articles)
            site.update_ids = json.dumps(list(recent_articles))
            site.update_time = get_site_last_id(site.pk)

            if user:
                site.unread_count = get_user_unread_count(user.oauth_id, recent_articles)

        context = dict()
        context['pg'] = pg
        context['sites'] = sites
        context['num_pages'] = num_pages
        context['user'] = user

        return render(request, 'left/site_view.html', context=context)

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
    onlyunread = request.POST.get('onlyunread', 'no') == 'yes'

    user = get_login_user(request)

    # 我的订阅源
    if user is None:
        my_sub_feeds = get_visitor_subscribe_feeds(tuple(sub_feeds), tuple(unsub_feeds))
    else:
        my_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

    # 获取文章索引列表
    my_articles = set()
    for site_id in my_sub_feeds:
        my_articles.update(get_recent_site_articles(site_id))

    # 过滤
    if user and onlyunread:
        my_articles = get_user_unread_articles(user.oauth_id, my_articles)

    my_articles = sorted(my_articles, reverse=True)

    if my_articles:
        # 分页处理
        try:
            paginator_obj = Paginator(my_articles, page_size)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseForbidden("Page Number Error")

        pg = paginator_obj.page(page)
        num_pages = paginator_obj.num_pages

        articles = Article.objects.filter(uindex__in=pg.object_list).order_by('-id')[:50]

        context = dict()
        context['articles'] = articles
        context['num_pages'] = num_pages
        context['user'] = user
        context['pg'] = pg

        if mobile:
            return render(request, 'mobile/list.html', context=context)
        else:
            return render(request, 'left/list_view.html', context=context)

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
    recent_articles = list(get_recent_site_articles(site.pk))

    # 查看文章数限制
    site_articles_limit = 9999
    if user:
        if user.level < 10:
            site_articles_limit = settings.USER_SITE_ARTICLES_LIMIT
    else:
        site_articles_limit = settings.VISITOR_SITE_ARTICLES_LIMIT

    site_articles = Article.objects.filter(site=site, status='active').order_by('-id')[:site_articles_limit]

    if site_articles:
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
            context['articles'] = json.dumps(recent_articles)

            return render(request, 'left/list2_view.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{site_id}")
            return HttpResponseForbidden("Page Number Error")

    return HttpResponseForbidden("No Sites Data")


@verify_request
def get_recommend_articles(request):
    """
    获取文章推荐的订阅源，只开放登录用户 TODO 优化性能
    :param request:
    :return:
    """
    uindex = int(request.POST['id'])
    user = get_login_user(request)

    if uindex and user:
        recommend_articles = []
        relative_articles = list(get_similar_article(uindex).keys())
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

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
