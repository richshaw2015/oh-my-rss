
from django.http import HttpResponseNotFound, HttpResponseServerError, JsonResponse, HttpResponseForbidden
import django
from web.models import *
from web.utils import incr_view_star, get_visitor_subscribe_feeds, get_user_subscribe_feeds, get_login_user, \
    add_user_sub_feeds, del_user_sub_feed, get_user_unread_count, get_host_name, \
    set_user_read_articles, set_user_visit_day, set_user_stared, is_user_stared, is_podcast_feed, \
    get_recent_site_articles, set_user_site_cname, set_user_site_author, set_active_site
from web.views.views_html import get_all_issues
from web.verify import verify_request
import logging
from django.conf import settings
from web.rssparser.mpwx import add_ershicimi_feed, add_wemp_feed, add_chuansongme_feed, add_anyv_feed
from web.rssparser.atom import add_atom_feed, add_self_feed, add_qnmlgb_feed
from web.rssparser.podcast import add_postcast_feed
from web.tasks import update_sites_async
import json
import django_rq
import feedparser

logger = logging.getLogger(__name__)


@verify_request
def get_lastweek_articles(request):
    """
    游客用户返回过去一周的文章 id 列表；登录用户返回过去一周的未读数
    """
    uid = request.POST.get('uid', '')
    user = get_login_user(request)
    sub_feeds = json.loads(request.POST.get('sub_feeds') or '[]')
    unsub_feeds = json.loads(request.POST.get('unsub_feeds') or '[]')
    ext = request.POST.get('ext', '')

    reach_sub_limit = False

    logger.info(f"查询未读数：`{uid}`{ext}")

    if user is None:
        my_sub_feeds = get_visitor_subscribe_feeds(tuple(sub_feeds), tuple(unsub_feeds))
        reach_sub_limit = len(my_sub_feeds) == settings.VISITOR_SUBS_LIMIT
    else:
        my_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

        if user.level < 10:
            reach_sub_limit = len(my_sub_feeds) == settings.USER_SUBS_LIMIT

    # 异步更新任务
    django_rq.enqueue(update_sites_async, list(my_sub_feeds), result_ttl=1, ttl=3600, failure_ttl=3600)

    # 获取文章索引列表
    my_toread_articles = set()
    for site_id in my_sub_feeds:
        my_toread_articles.update(get_recent_site_articles(site_id))

    my_toread_articles = list(my_toread_articles)

    if user:
        my_unread_count = get_user_unread_count(user.oauth_id, my_toread_articles)

        # 标记用户登陆
        set_user_visit_day(user.oauth_id)

        response = JsonResponse({"result": my_unread_count})
        if reach_sub_limit:
            response.set_signed_cookie('toast', 'SUBS_LIMIT_ERROR_MSG', max_age=20)

        return response
    else:
        response = JsonResponse({"result": my_toread_articles})
        if reach_sub_limit:
            response.set_signed_cookie('toast', 'SUBS_LIMIT_ERROR_MSG', max_age=20)

        return response


@verify_request
def add_view_stats(request):
    """
    增加文章浏览数据打点
    """
    uindex = request.POST.get('id')

    if incr_view_star('VIEW', uindex):
        return JsonResponse({})

    return HttpResponseNotFound("Param Error")


@verify_request
def leave_a_message(request):
    """
    添加留言
    """
    uid = request.POST.get('uid', '').strip()[:100]

    content = request.POST.get('content', '').strip()[:500]
    nickname = request.POST.get('nickname', '').strip()[:20]
    contact = request.POST.get('contact', '').strip()[:50]

    user = get_login_user(request)

    if content:
        try:
            msg = Message(uid=uid, content=content, nickname=nickname, contact=contact, user=user)
            msg.save()

            logger.warning(f"有新的留言：`{content}")

            return get_all_issues(request)
        except:
            logger.error(f"留言增加失败：`{uid}`{content}`{nickname}`{contact}")

            return HttpResponseServerError('Internal Error')

    logger.warning(f"参数错误：`{content}")
    return HttpResponseNotFound("Param Error")


@verify_request
def submit_a_feed(request):
    """
    用户添加一个自定义的订阅源
    """
    feed_url = request.POST.get('url', '').strip()[:1024]
    user = get_login_user(request)

    if feed_url:
        host = get_host_name(feed_url)

        if settings.ERSHICIMI_HOST in host:
            feed_url = feed_url.replace('/user/analysis?bid=', '/a/')
            rsp = add_ershicimi_feed(feed_url)
        elif host in settings.ALLOWED_HOSTS:
            rsp = add_self_feed(feed_url)
        elif settings.QNMLGB_HOST in host:
            rsp = add_qnmlgb_feed(feed_url)
        elif settings.WEMP_HOST in host:
            rsp = add_wemp_feed(feed_url)
        elif settings.CHUANSONGME_HOST in host:
            rsp = add_chuansongme_feed(feed_url)
        elif settings.ANYV_HOST in host:
            rsp = add_anyv_feed(feed_url)
        else:
            # 区分播客还是普通 RSS
            feed_obj = feedparser.parse(feed_url)

            if is_podcast_feed(feed_obj):
                rsp = add_postcast_feed(feed_obj)
            else:
                rsp = add_atom_feed(feed_obj)

        if rsp:
            logger.warning(f"有新订阅源被提交：`{feed_url}")

            set_active_site(rsp['site'])

            # 已登录用户，自动订阅
            if user:
                add_user_sub_feeds(user.oauth_id, [rsp['site'], ])

            if rsp.get('creator') == 'user':
                # 新增的普通 RSS 才触发异步更新任务
                django_rq.enqueue(update_sites_async, [rsp['site'], ], result_ttl=1, ttl=3600, failure_ttl=3600)

            return JsonResponse(rsp)
        else:
            logger.warning(f"RSS 解析失败：`{feed_url}")

    return HttpResponseNotFound("Param Error")


@verify_request
def user_subscribe_feed(request):
    """
    已登录用户订阅源
    """
    site_id = request.POST.get('site_id', '').strip()[:32]

    user = get_login_user(request)
    site = Site.objects.get(pk=site_id, status='active')

    if user and site:
        # 先判断是否达到限制
        if user.level < 10:
            if len(get_user_subscribe_feeds(user.oauth_id, from_user=False, user_level=user.level)) \
                    == settings.USER_SUBS_LIMIT:

                logger.warning(f"已达到订阅上限：`{user.oauth_name}")
                return JsonResponse({"code": 1, "msg": f"已达到 {settings.USER_SUBS_LIMIT} 个订阅数，请先取消一部分！"})

        add_user_sub_feeds(user.oauth_id, [site_id, ])

        # 异步更新
        django_rq.enqueue(update_sites_async, [site.pk, ], result_ttl=1, ttl=3600, failure_ttl=3600)

        logger.warning(f"登陆用户订阅动作：`{user.oauth_name}`{site_id}")

        return JsonResponse({"code": 0, "msg": '订阅成功 ^o^'})

    return HttpResponseForbidden("Param Error")


@verify_request
def user_unsubscribe_feed(request):
    """
    已登录用户取消订阅源
    """
    site_id = request.POST.get('site_id', '').strip()[:32]
    user = get_login_user(request)

    if user and site_id:
        del_user_sub_feed(user.oauth_id, site_id)

        logger.warning(f"登陆用户取消订阅动作：`{user.oauth_name}`{site_id}")

        return JsonResponse({"site": site_id})

    return HttpResponseForbidden("Param Error")


@verify_request
def user_custom_site(request):
    """
    用户自定义源名称
    """
    site_id = request.POST.get('site_id', '').strip()[:32]
    site_name = request.POST.get('site_name', '').strip()[:20]
    site_author = request.POST.get('site_author', '').strip()[:20]

    user = get_login_user(request)

    if user and site_id:
        logger.warning(f"用户自定义订阅源：`{site_id}`{site_name}`{site_author}")

        set_user_site_cname(user.oauth_id, site_id, site_name)
        set_user_site_author(user.oauth_id, site_id, site_author)

        return JsonResponse({})

    return HttpResponseForbidden("Param Error")


@verify_request
def user_mark_read_all(request):
    """
    设置批量已读，如不传 ids 则设置全部已读
    """
    ids = json.loads(request.POST.get('ids') or '[]')
    user = get_login_user(request)

    if user:
        if not ids:
            my_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

            ids = set()
            for site_id in my_sub_feeds:
                ids.update(get_recent_site_articles(site_id))

        set_user_read_articles(user.oauth_id, ids)

        if ids:
            return get_lastweek_articles(request)
        else:
            return JsonResponse({})

    return HttpResponseNotFound("Param Error")


@verify_request
def user_force_update_site(request):
    """
    强制刷新源，用户手动触发
    """
    site_id = request.POST.get('site_id', '')

    site = Site.objects.get(pk=site_id, status='active')

    if site:
        # 异步刷新
        logger.info(f"强制刷新源：`{site_id}")
        django_rq.enqueue(update_sites_async, [site.pk, ], True, result_ttl=1, ttl=3600, failure_ttl=3600)

        return JsonResponse({})

    return HttpResponseNotFound("Param Error")


@verify_request
def user_star_article(request):
    """
    登陆用户收藏文章
    """
    uindex = request.POST.get('id')
    user = get_login_user(request)

    if user and uindex:
        if not is_user_stared(user.oauth_id, uindex):
            article = Article.objects.get(uindex=uindex, status='active')

            try:
                record = UserArticle(user=user, site=article.site, uindex=uindex, title=article.title,
                                     author=article.author, src_url=article.src_url)
                record.save()
            except django.db.utils.IntegrityError:
                logger.warning(f"已经收藏过了：`{user.oauth_id}`{uindex}")
                return JsonResponse({})

            # 缓存标记
            set_user_stared(user.oauth_id, uindex)

            # 统计次数
            incr_view_star('STAR', uindex)

            return JsonResponse({})
        else:
            return JsonResponse({})
    return HttpResponseNotFound("Param Error")
