from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError, JsonResponse
from .models import *
from datetime import date, timedelta
from .utils import incr_redis_key, get_page_uv
from .views_api import get_issues_html


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

    # time.sleep(2)

    # 分页处理
    paginator_obj = Paginator(my_articles, page_size)
    if my_articles:
        try:
            # 页面及数据
            pg = paginator_obj.page(page)
            num_pages = paginator_obj.num_pages
            uv = get_page_uv(pg)

            context = dict()
            context['pg'] = pg
            context['uv'] = uv
            context['num_pages'] = num_pages
            return render(request, 'left/../tmpl/ajax/list.html', context=context)
        except:
            return HttpResponseNotFound("分页参数错误")
    return HttpResponseNotFound("没有订阅任何内容")


def get_my_lastweek_articles(request):
    """
    过去一周的文章id列表
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')

    lastweek_date = date.today() - timedelta(days=7)
    my_sub_sites = get_sub_sites(sub_feeds, unsub_feeds)
    my_lastweek_articles = list(Article.objects.filter(status='active', site__name__in=my_sub_sites,
                                                       ctime__gte=lastweek_date).values_list('uindex', flat=True))
    return JsonResponse({"result": my_lastweek_articles})


def log_action(request):
    """
    增加文章浏览数据打点
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')
    uindex = request.POST.get('id')
    action = request.POST.get('action')

    if incr_redis_key(action, uindex):
        return JsonResponse({})
    else:
        return HttpResponseNotFound("类型错误")


def leave_a_message(request):
    """
    添加留言
    :param request:
    :return:
    """
    uid = request.POST.get('uid', '').strip()[:100]
    content = request.POST.get('content', '').strip()[:500]
    nickname = request.POST.get('nickname', '').strip()[:20]
    contact = request.POST.get('contact', '').strip()[:50]

    if uid and content:
        try:
            msg = Message(uid=uid, content=content, nickname=nickname, contact=contact)
            msg.save()
            return get_issues_html(request)
        except:
            return HttpResponseServerError('内部错误')

    return HttpResponseNotFound("参数错误")
