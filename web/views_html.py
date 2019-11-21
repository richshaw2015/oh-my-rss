from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, HttpResponseServerError
from .models import *
from .utils import get_page_uv, get_subscribe_sites
from .verify import verify_request
import logging

logger = logging.getLogger(__name__)


@verify_request
def get_article_detail(request):
    """
    获取文章详情
    """
    uindex = request.POST.get('id')
    mobile = request.POST.get('mobile', False)

    try:
        article = Article.objects.get(uindex=uindex)

        context = dict()
        context['article'] = article

        if mobile:
            return render(request, 'mobile/article.html', context=context)
        else:
            return render(request, 'article/index.html', context=context)
    except:
        logger.warning(f"获取文章详情请求处理异常：`{uindex}")
    return HttpResponseNotFound("Param error")


@verify_request
def get_all_feeds(request):
    """
    获取订阅列表
    """
    show_feeds = Site.objects.filter(status='active', star__gte=9).order_by('-star')
    hide_feeds = Site.objects.filter(status='active', star__lt=9).order_by('-star')

    try:
        last_site = Site.objects.filter(status='active', creator='user', star__gte=9).order_by('-ctime')[0]
        submit_tip = f"「{last_site.cname[:20]}」({last_site.rss[:50]}) 最后被用户提交"
    except:
        submit_tip = '提交RSS源，例如：https://coolshell.cn/feed'

    context = dict()
    context['show_feeds'] = show_feeds
    context['hide_feeds'] = hide_feeds
    context['submit_tip'] = submit_tip

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
    获取我的文章列表
    """
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))
    mobile = request.POST.get('mobile', False)

    # 个人订阅处理
    my_sub_sites = get_subscribe_sites(tuple(sub_feeds), tuple(unsub_feeds))
    my_articles = Article.objects.all().prefetch_related('site').filter(
        status='active', site__name__in=my_sub_sites).order_by('-id')[:500]

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
            if mobile:
                return render(request, 'mobile/list.html', context=context)
            else:
                return render(request, 'list.html', context=context)
        except:
            logger.warning(f"分页参数错误：`{page}`{page_size}`{sub_feeds}`{unsub_feeds}")
            return HttpResponseNotFound("Page number error")
    logger.warning("没有订阅任何内容")
    return HttpResponseNotFound("No Feeds subscribed")
