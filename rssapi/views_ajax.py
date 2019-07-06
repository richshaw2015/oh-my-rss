from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseNotFound
from .models import *
import time


def get_sub_sites(sub_feeds, unsub_feeds):
    """
    获取订阅的站点，已订阅 + 推荐 - 取消订阅
    TODO 增加缓存处理
    :param sub_feeds:
    :param unsub_feeds:
    :return:
    """
    recommend_feeds = list(Site.objects.filter(status='active', star__gte=20).values_list('name', flat=True))
    return list(set(sub_feeds + recommend_feeds) - set(unsub_feeds))


def get_my_article_list(request):
    """
    获取我的文章列表
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')
    page_size = int(request.POST.get('page_size', 10))
    page = int(request.POST.get('page', 1))

    # 个人订阅处理
    my_sub_sites = get_sub_sites(sub_feeds, unsub_feeds)
    my_articles = Article.objects.filter(status='active', site__name__in=my_sub_sites).order_by('-id')

    time.sleep(2)

    # 分页处理
    paginator_obj = Paginator(my_articles, page_size)
    if my_articles:
        try:
            pg = paginator_obj.page(page)
            num_pages = paginator_obj.num_pages

            context = dict()
            context['pg'] = pg
            context['num_pages'] = num_pages
            return render(request, 'ajax-left-list.html', context=context)
        except:
            return HttpResponseNotFound("分页参数错误")
    return HttpResponseNotFound("没有订阅任何内容")
