from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from .models import *
from .utils import get_page_uv, get_subscribe_sites, get_login_user, get_user_sub_feeds, set_user_read_article, \
    get_similar_article, get_feed_ranking_dict, get_user_unread_count
from .verify import verify_request
import logging
from collections import defaultdict
from .sql import *

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
def get_all_feeds(request):
    """
    获取订阅列表，已登录用户默认展示已订阅内容；区分已订阅、未订阅
    """
    user = get_login_user(request)
    
    if user is None:
        # 游客按照推荐和普通
        sub_sites = Site.objects.filter(status='active', star__gte=20).order_by('-star')
        unsub_sites = Site.objects.filter(status='active', star__lt=20).order_by('-star')
    else:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)
        sub_sites = Site.objects.filter(status='active', name__in=user_sub_feeds).order_by('-star')
        unsub_sites = Site.objects.filter(status='active').exclude(name__in=user_sub_feeds).\
            exclude(star__lt=8).order_by('-star')

    try:
        last_site = Site.objects.filter(status='active', creator='user', star__gte=9).order_by('-ctime')[0]
        submit_tip = f"「{last_site.cname[:20]}」({last_site.rss[:50]}) 最后被用户提交"
    except:
        submit_tip = '提交 RSS 源，例如：https://coolshell.cn/feed'

    context = dict()
    context['sub_sites'] = sub_sites
    context['unsub_sites'] = unsub_sites
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
def get_recent_articles(request):
    """
    获取最近更新内容
    """
    user = get_login_user(request)
    recommend = request.POST.get('recommend', 'recommend')

    if recommend == 'unrecommend':
        articles = Article.objects.raw(get_other_articles_sql)
    elif recommend == 'recommend':
        articles = Article.objects.raw(get_recommend_articles_sql)
    else:
        logger.warning(f'未知的类型：{recommend}')

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

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
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

    sites = Site.objects.filter(status='active').order_by('-id')[:100]
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
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

    sites = Site.objects.filter(status='active').order_by('-id')[:100]
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
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

    feed_ranking = get_feed_ranking_dict()

    context = dict()

    context['user'] = user
    context['feed_ranking'] = feed_ranking
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'explore/feed_ranking.html', context=context)


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
    获取更新的全局站点视图
    """
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))

    user = get_login_user(request)

    if user is None:
        sub_update_sites = get_subscribe_sites(tuple(sub_feeds), tuple(unsub_feeds))
        sites = Article.objects.raw(site_update_view_sql % (str(tuple(sub_update_sites)), 100))
    else:
        sub_update_sites = get_user_sub_feeds(user.oauth_id)
        sites = Article.objects.raw(site_update_view_sql % (str(tuple(sub_update_sites)), 200))

    if sites:
        # 分页处理
        paginator_obj = Paginator(sites, page_size)

        try:
            # 页面及数据
            pg = paginator_obj.page(page)
            num_pages = paginator_obj.num_pages

            # 计算未读数
            pg_sites = set()
            for article in pg.object_list:
                pg_sites.add(article.site.name)

            pg_article_list = Article.objects.filter(status='active', is_recent=True, site__name__in=pg_sites).\
                values_list('site__name', 'uindex')

            pg_unread_dict = defaultdict(list)
            for k, v in pg_article_list:
                pg_unread_dict[k].append(v)

            pg_unread_count_dict = {}
            if user:
                for (name, articles) in pg_unread_dict.items():
                    pg_unread_count_dict[name] = get_user_unread_count(user.oauth_id, articles)

            context = dict()
            context['pg'] = pg
            context['num_pages'] = num_pages
            context['user'] = user
            context['pg_unread_dict'] = pg_unread_dict
            context['pg_unread_count_dict'] = pg_unread_count_dict

            return render(request, 'left/site_view.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseNotFound("Page Number Error")

    return HttpResponseNotFound("No Feeds Subscribed")


@verify_request
def get_article_update_view(request):
    """
    获取更新的文章列表视图，游客展示默认推荐内容；登录用户展示其订阅内容
    """
    # 请求参数获取
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))
    mobile = request.POST.get('mobile', False)

    user = get_login_user(request)

    if user is None:
        visitor_sub_sites = get_subscribe_sites(tuple(sub_feeds), tuple(unsub_feeds))

        my_articles = Article.objects.all().prefetch_related('site').filter(
            status='active', is_recent=True, site__name__in=visitor_sub_sites).order_by('-id')[:300]
    else:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

        if not user_sub_feeds:
            logger.warning(f'用户未订阅任何内容：`{user.oauth_name}')

        # TODO 这个 sql 比较耗时
        my_articles = Article.objects.all().prefetch_related('site').filter(
            status='active', is_recent=True, site__name__in=user_sub_feeds).order_by('-id')[:999]

    if my_articles:
        # 分页处理
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
                return render(request, 'left/list_view.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseNotFound("Page Number Error")

    return HttpResponseNotFound("No Feeds Subscribed")


@verify_request
def get_site_article_update_view(request):
    """
    获取某个站点的更新文章列表视图
    """
    # 请求参数获取
    site_name = request.POST.get('site_name', '')
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))

    user = get_login_user(request)

    site = Site.objects.get(name=site_name, status='active')

    if user:
        site_articles = Article.objects.all().prefetch_related('site').filter(
            status='active', site__name=site_name).order_by('-id')[:200]
    else:
        site_articles = Article.objects.all().prefetch_related('site').filter(
            status='active', site__name=site_name).order_by('-id')[:100]

    if site_articles:
        articles = [article.uindex for article in site_articles]

        # 分页处理
        paginator_obj = Paginator(site_articles, page_size)
        try:
            # 页面及数据
            pg = paginator_obj.page(page)
            num_pages = paginator_obj.num_pages
            uv = get_page_uv(pg)

            context = dict()
            context['pg'] = pg
            context['uv'] = uv
            context['num_pages'] = num_pages
            context['site'] = site
            context['user'] = user
            context['articles'] = articles

            return render(request, 'left/list2_view.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{site_name}")
            return HttpResponseNotFound("Page Number Error")

    return HttpResponseNotFound("No Sites Data")


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
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

        for relative_uindex in relative_articles:
            try:
                article = Article.objects.get(uindex=relative_uindex)
            except:
                continue

            if article.site.name not in user_sub_feeds:
                recommend_articles.append(article)
            if len(recommend_articles) >= 3:
                break

        if recommend_articles:
            logger.info(f'推荐数据条数：`{len(recommend_articles)}`{user.oauth_name}')

            context = dict()
            context['recommend_articles'] = recommend_articles

            return render(request, 'recommend/relative_article.html', context=context)

    return HttpResponseNotFound("No Recommend Data")
