
from django.http import HttpResponseNotFound, HttpResponseServerError, JsonResponse
from .models import *
from datetime import date, timedelta
from .utils import incr_redis_key, get_subscribe_sites
from .views_html import get_all_issues
from .verify import verify_request
import logging

logger = logging.getLogger(__name__)


@verify_request
def get_lastweek_articles(request):
    """
    过去一周的文章id列表
    """
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')

    logger.info(f"收到订阅源查询请求：`{sub_feeds}`{unsub_feeds}")

    lastweek_date = date.today() - timedelta(days=7)
    
    my_sub_feeds = get_subscribe_sites(sub_feeds, unsub_feeds)
    my_lastweek_articles = list(Article.objects.filter(status='active', site__name__in=my_sub_feeds,
                                                       ctime__gte=lastweek_date).values_list('uindex', flat=True))
    return JsonResponse({"result": my_lastweek_articles})


@verify_request
def add_log_action(request):
    """
    增加文章浏览数据打点
    """
    uindex = request.POST.get('id')
    action = request.POST.get('action')

    if incr_redis_key(action, uindex):
        return JsonResponse({})
    else:
        logger.warning(f"打点增加失败：`{uindex}`{action}")
        return HttpResponseNotFound("Param error")


@verify_request
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
            logger.error(f"留言增加失败：`{uid}`{content}`{nickname}`{contact}")
            return HttpResponseServerError('Inter error')

    logger.warning(f"参数错误：`{uid}`{content}")
    return HttpResponseNotFound("Param error")
