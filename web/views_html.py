from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from .models import *
from .utils import get_page_uv, get_subscribe_sites, get_login_user, get_user_sub_feeds, set_user_read_article, \
    get_similar_article
from .verify import verify_request
import logging
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
        logger.warning(f"获取文章详情请求处理异常：`{uindex}")
        return HttpResponseNotFound("Param error")

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

    articles = Article.objects.raw(get_recommend_articles_sql)

    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

    context = dict()
    context['articles'] = articles
    context['user'] = user
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

    sites = Site.objects.filter(status='active').order_by('-id')[:50]
    context = dict()

    context['user'] = user
    context['sites'] = sites
    context['user_sub_feeds'] = user_sub_feeds

    return render(request, 'explore/recent_sites.html', context=context)


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

    if user is None:
        visitor_sub_sites = get_subscribe_sites(tuple(sub_feeds), tuple(unsub_feeds))

        my_articles = Article.objects.all().prefetch_related('site').filter(
            status='active', is_recent=True, site__name__in=visitor_sub_sites).order_by('-id')[:300]
    else:
        user_sub_feeds = get_user_sub_feeds(user.oauth_id)

        if not user_sub_feeds:
            logger.warning(f'用户未订阅任何内容：`{user.oauth_id}')

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
                return render(request, 'list.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseNotFound("Page number error")

    return HttpResponseNotFound("No Feeds subscribed")


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
            article = Article.objects.get(uindex=relative_uindex)

            if article.site.name not in user_sub_feeds:
                recommend_articles.append(article)
            if len(recommend_articles) >= 2:
                break

        if recommend_articles:
            logger.info(f'推荐数据条数：`{len(recommend_articles)}`{user.oauth_name}')

            context = dict()
            context['recommend_articles'] = recommend_articles

            return render(request, 'recommend/relative_article.html', context=context)

    return HttpResponseNotFound("No Recommend Data")
