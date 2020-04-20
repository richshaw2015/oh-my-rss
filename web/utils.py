# -*- coding: utf-8 -*-

import time
import redis
from functools import lru_cache
from django.conf import settings
from django.urls import reverse
from .models import Site, User
import requests
import os
from PIL import Image
from io import BytesIO
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import logging
import hashlib
import urllib
from collections import Counter
from urllib.parse import urlparse

# init Redis connection
R = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_WEB_DB, decode_responses=True)
logger = logging.getLogger(__name__)


def get_host_name(url):
    return urlparse(url).netloc


def incr_action(action, uindex):
    """
    add operate
    :param key:
    :param uindex:
    :return:
    """
    key = None
    if action == 'VIEW':
        key = settings.REDIS_VIEW_KEY % uindex
    elif action == 'THUMB':
        key = settings.REDIS_THUMB_KEY % uindex
    elif action == 'OPEN':
        key = settings.REDIS_OPEN_KEY % uindex

    if key is not None:
        try:
            return R.incr(key, amount=1)
        except:
            logger.error(f"写入Redis出现异常：`{key}")
    return False


def add_register_count():
    """
    注册用户数统计
    :return:
    """
    key = settings.REDIS_REG_KEY % current_day()

    return incr_redis_key(key)


def add_api_profile(api, elapsed):
    """
    按天进行平均耗时计算
    :param api:
    :param elapsed:
    :return:
    """
    day = current_day()
    count = total = 0
    try:
        R.sadd(settings.REDIS_API_KEY, api)

        count = R.incr(settings.REDIS_API_COUNT_KEY % (api, day))
        total = R.incr(settings.REDIS_API_TOTAL_KEY % (api, day), amount=elapsed)
        R.set(settings.REDIS_API_AVG_KEY % (api, day), int(total/count))
    except:
        logger.error(f"api 平均耗时计算异常！`{count}`{total}")


def get_page_uv(page):
    """
    get all visit data of current page
    :param page:
    :return:
    """
    key_list, data_list = [], []
    for article in page.object_list:
        key_list.extend([settings.REDIS_VIEW_KEY % article.uindex, settings.REDIS_THUMB_KEY % article.uindex,
                         settings.REDIS_OPEN_KEY % article.uindex])
    try:
        data_list = R.mget(*key_list)
    except:
        logger.error("Redis连接异常")
    return dict(zip(key_list, data_list))


@lru_cache(maxsize=4)
def get_profile_apis():
    return (
        reverse('get_articles_list'), reverse('get_lastweek_articles'), reverse('get_explore'),
        reverse('get_recent_articles'),
    )


def set_active_rss(feeds):
    """
    访问过的源，设置一个标识
    :param feeds:
    :return:
    """
    with R.pipeline(transaction=False) as p:
        for feed in feeds:
            p.set(settings.REDIS_ACTIVE_RSS_KEY % feed, 1, 3*24*3600)
        p.execute()


def is_active_rss(feed):
    return R.get(settings.REDIS_ACTIVE_RSS_KEY % feed) == '1'


@lru_cache(maxsize=128, typed=True)
def get_subscribe_sites(sub_feeds, unsub_feeds, star=20):
    """
    获取游客订阅的站点，已订阅 + 推荐 - 取消订阅
    :param sub_feeds:
    :param unsub_feeds:
    :param star:
    :return:
    """
    # 设置订阅源缓存
    set_active_rss(sub_feeds)

    recommend_feeds = list(Site.objects.filter(status='active', star__gte=star).values_list('name', flat=True))
    return list(set(list(sub_feeds) + recommend_feeds) - set(unsub_feeds))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_hash_name(feed_id):
    """
    用户提交的订阅源，根据hash值生成唯一标识
    """
    return hashlib.md5(feed_id.encode('utf8')).hexdigest()


def current_day():
    return time.strftime("%Y%m%d", time.localtime(time.time()))


def is_visit_today(uid):
    """
    当天是否访问过
    :param uid:
    :return:
    """
    key = settings.REDIS_VISIT_KEY % (current_day(), uid)
    try:
        return R.get(key)
    except:
        logger.error(f"写入Redis出现异常：`{key}")
    return False


def set_visit_today(uid):
    key = settings.REDIS_VISIT_KEY % (current_day(), uid)
    try:
        return R.set(key, 1, 24*3600+100)
    except:
        logger.error(f"写入Redis出现异常：`{key}")


def is_old_user(uid):
    """
    是否是老用户（过去一周）
    :param uid:
    :return:
    """
    key = settings.REDIS_WEEK_KEY % uid
    try:
        return R.get(settings.REDIS_WEEK_KEY % uid)
    except:
        logger.error(f"写入Redis出现异常：`{key}")
    return False


def set_old_user(uid):
    key = settings.REDIS_WEEK_KEY % uid
    try:
        return R.set(key, 1, 7*24*3600)
    except:
        logger.error(f"写入Redis出现异常：`{key}")


def incr_redis_key(key):
    try:
        return R.incr(key, amount=1)
    except:
        logger.error(f"写入Redis出现异常：`{key}")


def add_refer_host(host):
    key = settings.REDIS_REFER_ALL_KEY
    try:
        return R.sadd(key, host)
    except:
        logger.error(f"写入Redis出现异常：`{key}")


def log_refer_request(request):
    referer = request.META.get('HTTP_REFERER', '')
    if referer:
        host = get_host_name(referer)

        if host and host not in settings.ALLOWED_HOSTS:
            logger.info(f"收到外域来源：`{host}`{referer}")
            try:
                add_refer_host(host)
                incr_redis_key(settings.REDIS_REFER_PV_KEY % host)
                incr_redis_key(settings.REDIS_REFER_PV_DAY_KEY % (host, current_day()))
            except:
                logger.error("外域请求统计异常")


def add_user_sub_feeds(oauth_id, feeds):
    key = settings.REDIS_USER_SUB_KEY % oauth_id
    try:
        return R.sadd(key, *feeds)
    except:
        logger.error(f"写入Redis出现异常：`{key}")


def del_user_sub_feed(oauth_id, feed):
    key = settings.REDIS_USER_SUB_KEY % oauth_id
    try:
        return R.srem(key, feed)
    except:
        logger.error(f"写入Redis出现异常：`{key}")


def get_user_sub_feeds(oauth_id):
    key = settings.REDIS_USER_SUB_KEY % oauth_id
    try:
        sub_feeds = R.smembers(key)

        # 设置订阅源缓存
        set_active_rss(sub_feeds)

        return sub_feeds
    except:
        logger.error(f"写入Redis出现异常：`{key}")
    return []


def set_user_read_article(oauth_id, uindex):
    """
    已登录用户同步已读文章状态
    """
    key = settings.REDIS_USER_READ_KEY % (oauth_id, uindex)
    try:
        return R.set(key, 1, 14*24*3600)
    except:
        logger.error(f"写入Redis出现异常：`{key}")
    return None


def get_user_unread_articles(oauth_id, articles):
    """
    获取用户过去一周未读的文章列表
    """
    user_read_keys = [settings.REDIS_USER_READ_KEY % (oauth_id, uindex) for uindex in articles]
    user_unread_list = []

    if articles:
        try:
            user_read_info_dict = dict(zip(articles, R.mget(*user_read_keys)))
            for article in articles:
                if user_read_info_dict.get(article) is None:
                    user_unread_list.append(article)
        except:
            logger.error(f"获取用户未读文章列表异常：`{oauth_id}")

    return user_unread_list


def get_login_user(request):
    """
    获取已登录用户信息
    :param request:
    :return: 获取成功返回 User 对象；用户不存在则返回 None
    """
    oauth_id = request.get_signed_cookie('oauth_id', False)
    # oauth_id = 'github/28855629'

    if oauth_id:
        try:
            return User.objects.get(oauth_id=oauth_id, status='active')
        except:
            logger.warning(f'用户不存在：`{oauth_id}')
    return None


def save_avatar(avatar, userid, size=100):
    """
    保存网络头像
    :param avatar:
    :param userid:
    :param size:
    :return: 保存后的头像地址
    """
    try:
        rsp = requests.get(avatar, timeout=10)

        if rsp.ok:
            img_obj = Image.open(BytesIO(rsp.content))
            img_obj.thumbnail((size, size))
            jpg = get_hash_name(userid) + '.jpg'

            if img_obj.mode != 'RGB':
                img_obj = img_obj.convert('RGB')

            img_obj.save(os.path.join(settings.BASE_DIR, 'assets', 'avatar', jpg))
            return f'/assets/avatar/{jpg}'
        else:
            logger.error(f"同步用户头像出现网络异常！`{userid}`{avatar}")
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        logger.error(f"同步用户头像网络异常！`{userid}`{avatar}")
    except:
        logger.error(f"同步用户头像未知异常`{userid}`{avatar}")

    return '/assets/img/logo.png'


def cal_cosine_distance(x, y):
    """
    计算两个列表的余弦相似度，0 ~ 1
    :param x:
    :param y:
    :return:
    """
    x_counter = Counter(x)
    y_counter = Counter(y)

    if x_counter == y_counter:
        return 1

    words = list(x_counter.keys() | y_counter.keys())

    x_vect = [x_counter.get(word, 0) for word in words]
    y_vect = [y_counter.get(word, 0) for word in words]

    len_x = sum(av*av for av in x_vect) ** 0.5
    len_y = sum(bv*bv for bv in y_vect) ** 0.5

    dot = sum(av*bv for av, bv in zip(x_vect, y_vect))

    distance = dot / (len_x * len_y)

    return round(distance, 2)


def get_similar_article(uindex):
    key = settings.REDIS_SIMILAR_ARTICLE_KEY % uindex

    try:
        return R.hgetall(key)
    except:
        logger.error(f"读取 Redis 出现异常：`{key}")


def set_similar_article(uindex, simlar_dict):
    key = settings.REDIS_SIMILAR_ARTICLE_KEY % uindex

    try:
        ret = R.hmset(key, simlar_dict)
        R.expire(key, 30 * 24 * 3600)
        return ret
    except:
        logger.error(f"写入 Redis 出现异常：`{key}")


def generate_rss_avatar(url):
    """
    生成用户提交 RSS 源的默认头像
    :param url:
    :return:
    """
    avatar = "/assets/img/logo.png"
    host = get_host_name(url)

    if 'weibo.com' in host or 'weibo.cn' in host:
        avatar = "/assets/img/weibo.jpg"
    elif "jianshu.com" in host:
        avatar = "/assets/img/jianshu.png"
    elif host in ('blog.sina.com', 'blog.sina.com.cn'):
        avatar = '/assets/img/blogsina.jpg'
    elif 'twitter.com' in host:
        avatar = '/assets/img/twitter.png'
    elif 'youtube.com' in host:
        avatar = '/assets/img/youtube.png'
    elif host == 'music.163.com':
        avatar = '/assets/img/163music.jpg'
    elif 'douban.com' in host:
        avatar = '/assets/img/douban.png'
    elif 'zhihu.com' in host:
        avatar = '/assets/img/zhihu.png'
    elif 'bilibili.com' in host:
        avatar = '/assets/img/bilibili.png'
    elif host == 'xueqiu.com':
        avatar = '/assets/img/xueqiu.jpg'
    elif 'tophub.today' in host:
        avatar = '/assets/img/tophub.png'
    elif 'github.com' in host:
        avatar = '/assets/img/github.png'
    elif 'juejin.im' in host:
        avatar = '/assets/img/juejin.png'
    elif 'rsshub.app' in host:
        avatar = '/assets/img/rsshub.png'
    elif 'chuansongme.com' in host:
        avatar = '/assets/img/chuansongme.jpg'
    elif 'ximalaya.com' in host:
        avatar = '/assets/img/ximalaya.png'
    elif 'smzdm.com' in host:
        avatar = '/assets/img/smzdm.jpg'
    elif host == "qnmlgb.tech":
        avatar = '/assets/img/qnmlgb.png'
    elif host == 'weixin.sogou.com':
        avatar = '/assets/img/sogou.png'
    elif host == 'pubs.acs.org':
        avatar = '/assets/img/acs.png'

    return avatar


def vacuum_sqlite_db():
    """
    压缩空间
    :return:
    """
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("VACUUM")
    connection.close()
