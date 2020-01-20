
from django.http import HttpResponseNotFound, HttpResponseServerError, JsonResponse
from .models import *
from datetime import timedelta, datetime
from .utils import incr_action, get_subscribe_sites, get_user_sub_feeds, get_login_user, \
    add_user_sub_feeds, del_user_sub_feed
from .views_html import get_all_issues
from .verify import verify_request
import logging
import urllib
from web.omrssparser.wemp import parse_wemp_ershicimi
from web.omrssparser.atom import parse_atom

logger = logging.getLogger(__name__)


@verify_request
def get_lastweek_articles(request):
    """
    过去一周的文章id列表
    """
    uid = request.POST.get('uid', '')
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')
    ext = request.POST.get('ext', '')

    user = get_login_user(request)

    logger.info(f"收到订阅源查询请求：`{uid}`{unsub_feeds}`{ext}")

    lastweek_dt = datetime.now() - timedelta(days=7)

    if user is None:
        my_sub_feeds = get_subscribe_sites(tuple(sub_feeds), tuple(unsub_feeds))
    else:
        my_sub_feeds = get_user_sub_feeds(user.oauth_id)

    my_lastweek_articles = list(Article.objects.all().prefetch_related('site').filter(
        status='active', site__name__in=my_sub_feeds, ctime__gte=lastweek_dt).values_list('uindex', flat=True))

    return JsonResponse({"result": my_lastweek_articles})


@verify_request
def add_log_action(request):
    """
    增加文章浏览数据打点
    """
    uindex = request.POST.get('id')
    action = request.POST.get('action')

    if incr_action(action, uindex):
        return JsonResponse({})
    else:
        logger.warning(f"打点增加失败：`{uindex}`{action}")
        return HttpResponseNotFound("Param error")


@verify_request
def leave_a_message(request):
    """
    添加留言
    """
    # TODO 适配已登录用户
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


@verify_request
def submit_a_feed(request):
    """
    用户添加一个自定义的订阅源
    """
    feed_url = request.POST.get('url', '').strip()[:1024]
    user = get_login_user(request)

    if feed_url:
        host = urllib.parse.urlparse(feed_url).netloc

        if 'ershicimi.com' in host:
            rsp = parse_wemp_ershicimi(feed_url)
        else:
            rsp = parse_atom(feed_url)

        if rsp:
            # 已登录用户，自动订阅
            if user:
                add_user_sub_feeds(user.oauth_id, [rsp['name'], ])
            return JsonResponse(rsp)
        else:
            logger.warning(f"RSS 解析失败：`{feed_url}")

    return HttpResponseNotFound("Param error")


@verify_request
def user_subscribe_feed(request):
    """
    已登录用户订阅源
    """
    feed = request.POST.get('feed', '').strip()[:32]

    user = get_login_user(request)

    if user and feed:
        try:
            Site.objects.get(name=feed)
            add_user_sub_feeds(user.oauth_id, [feed, ])
            return JsonResponse({"name": feed})
        except:
            logger.warning(f'用户订阅出现异常：`{feed}`{user.oauth_id}')

    return HttpResponseNotFound("Param error")


@verify_request
def user_unsubscribe_feed(request):
    """
    已登录用户取消订阅源
    """
    feed = request.POST.get('feed', '').strip()[:32]

    user = get_login_user(request)

    if user and feed:
        del_user_sub_feed(user.oauth_id, feed)
        return JsonResponse({"name": feed})
    return HttpResponseNotFound("Param error")


# TODO 增加已登录用户的未读文章同步
