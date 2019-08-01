
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError, JsonResponse
from .models import *
from datetime import date, timedelta
from .utils import incr_redis_key, get_sub_sites
from .views_html import get_all_issues


def get_lastweek_articles(request):
    """
    过去一周的文章id列表
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')

    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')

    lastweek_date = date.today() - timedelta(days=7)
    
    my_sub_feeds = get_sub_sites(sub_feeds, unsub_feeds)
    my_lastweek_articles = list(Article.objects.filter(status='active', site__name__in=my_sub_feeds,
                                                       ctime__gte=lastweek_date).values_list('uindex', flat=True))
    return JsonResponse({"result": my_lastweek_articles})


def add_log_action(request):
    """
    增加文章浏览数据打点
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')

    uindex = request.POST.get('id')
    action = request.POST.get('action')

    if incr_redis_key(action, uindex):
        return JsonResponse({})
    else:
        return HttpResponseNotFound("Param error")


def leave_a_message(request):
    """
    添加留言
    """
    uid = request.POST.get('uid', '').strip()[:100]

    content = request.POST.get('content', '').strip()[:500]
    nickname = request.POST.get('nickname', '').strip()[:20]
    contact = request.POST.get('contact', '').strip()[:50]

    if uid and content:
        try:
            msg = Message(uid=uid, content=content, nickname=nickname, contact=contact)
            msg.save()
            return get_all_issues(request)
        except:
            return HttpResponseServerError('Inter error')

    return HttpResponseNotFound("Param error")
