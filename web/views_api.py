
from django.http import HttpResponseNotFound, HttpResponseServerError, JsonResponse
import django
from web.models import *
from web.utils import incr_view_star, get_subscribe_feeds, get_user_sub_feeds, get_login_user, \
    add_user_sub_feeds, del_user_sub_feed, get_user_unread_count, set_user_read_article, get_host_name, \
    set_user_read_articles, set_user_visit_day, set_user_stared, is_user_stared, write_dat_file
from web.views_html import get_all_issues
from web.verify import verify_request
import logging
from django.conf import settings
from web.omrssparser.wemp import parse_wemp_ershicimi
from web.omrssparser.atom import parse_atom, parse_self_atom
from web.tasks import update_sites_async

logger = logging.getLogger(__name__)


@verify_request
def get_lastweek_articles(request):
    """
    游客用户返回过去一周的文章 id 列表；登录用户返回过去一周的未读数
    """
    uid = request.POST.get('uid', '')
    user = get_login_user(request)
    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')
    ext = request.POST.get('ext', '')

    logger.info(f"过去一周文章查询：`{uid}`{unsub_feeds}`{ext}")

    if user is None:
        my_sub_feeds = get_subscribe_feeds(tuple(sub_feeds), tuple(unsub_feeds))
    else:
        my_sub_feeds = get_user_sub_feeds(user.oauth_id)

    my_lastweek_articles = list(Article.objects.filter(status='active', site__name__in=my_sub_feeds,
                                                       is_recent=True).values_list('uindex', flat=True))

    # 异步更新任务
    update_sites_async.delay(list(my_sub_feeds))

    if user:
        my_lastweek_unread_count = get_user_unread_count(user.oauth_id, my_lastweek_articles)

        # 标记用户登陆
        set_user_visit_day(user.oauth_id)
        return JsonResponse({"result": my_lastweek_unread_count})
    else:
        return JsonResponse({"result": my_lastweek_articles})


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

        if 'ershicimi.com' in host:
            feed_url = feed_url.replace('/user/analysis?bid=', '/a/')
            rsp = parse_wemp_ershicimi(feed_url)
        elif host in settings.ALLOWED_HOSTS:
            rsp = parse_self_atom(feed_url)
        else:
            rsp = parse_atom(feed_url)

        if rsp:
            logger.warning(f"有新订阅源被提交：`{feed_url}")

            # 已登录用户，自动订阅
            if user:
                add_user_sub_feeds(user.oauth_id, [rsp['name'], ])

            # 异步更新任务
            update_sites_async.delay([rsp['name']])

            return JsonResponse(rsp)
        else:
            logger.warning(f"RSS 解析失败：`{feed_url}")

    return HttpResponseNotFound("Param Error")


@verify_request
def user_subscribe_feed(request):
    """
    已登录用户订阅源
    """
    site_name = request.POST.get('feed', '').strip()[:32]

    user = get_login_user(request)
    site = Site.objects.get(name=site_name, status='active')

    if user and site:
        add_user_sub_feeds(user.oauth_id, [site_name, ])

        # 异步更新
        update_sites_async.delay([site_name, ])

        logger.warning(f"登陆用户订阅动作：`{user.oauth_name}`{site_name}")

        return JsonResponse({"name": site_name})

    return HttpResponseNotFound("Param Error")


@verify_request
def user_unsubscribe_feed(request):
    """
    已登录用户取消订阅源
    """
    site_name = request.POST.get('feed', '').strip()[:32]

    user = get_login_user(request)

    if user and site_name:
        del_user_sub_feed(user.oauth_id, site_name)

        logger.warning(f"登陆用户取消订阅动作：`{user.oauth_name}`{site_name}")

        return JsonResponse({"name": site_name})

    return HttpResponseNotFound("Param Error")


@verify_request
def user_mark_read_all(request):
    """
    设置批量已读，如不传 ids 则设置全部已读
    """
    uindexs = request.POST.get('ids', '')
    user = get_login_user(request)

    if user:
        if uindexs:
            uindexs = uindexs.split(',')
        else:
            my_sub_feeds = get_user_sub_feeds(user.oauth_id)

            uindexs = list(Article.objects.filter(status='active', site__name__in=my_sub_feeds, is_recent=True).
                       values_list('uindex', flat=True))

        set_user_read_articles(user.oauth_id, uindexs)

        return JsonResponse({})

    return HttpResponseNotFound("Param Error")


@verify_request
def user_force_update_site(request):
    """
    强制刷新源，用户手动触发
    """
    site_name = request.POST.get('site_name', '')
    user = get_login_user(request)

    site = Site.objects.get(name=site_name, status='active')

    if site and user:
        # 异步刷新
        update_sites_async.delay([site_name, ], True)

        return JsonResponse({})

    return HttpResponseNotFound("Param Error")


@verify_request
def user_mark_read_site(request):
    """
    设置站点全部已读
    """
    site_name = request.POST.get('site_name', '')
    user = get_login_user(request)

    site = Site.objects.get(name=site_name, status='active')

    if site and user:
        ids = Article.objects.filter(status='active', site__name=site_name, is_recent=True).\
            values_list('uindex', flat=True)

        # TODO 优化性能，批量设置已读
        for uindex in ids:
            set_user_read_article(user.oauth_id, uindex)

        # 返回未读数
        return get_lastweek_articles(request)

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

            # 收藏后的文章写入文件，防止丢失
            write_dat_file(uindex, article.content)

            # 缓存标记
            set_user_stared(user.oauth_id, uindex)

            # 统计次数
            incr_view_star('STAR', uindex)

            return JsonResponse({})
        else:
            return JsonResponse({})
    return HttpResponseNotFound("Param Error")
