# -*- coding: utf-8 -*-

import time
import redis
from functools import lru_cache
from django.conf import settings
from .models import Site
import logging
import hashlib

# init Redis connection
R = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_WEB_DB, decode_responses=True)
logger = logging.getLogger(__name__)


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
        except redis.exceptions.ConnectionError:
            logger.warning(f"写入Redis出现异常：`{key}")
    return False


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
    except redis.exceptions.ConnectionError:
        logger.error("Redis连接异常")
    return dict(zip(key_list, data_list))


@lru_cache(maxsize=128, typed=True)
def get_subscribe_sites(sub_feeds, unsub_feeds):
    """
    获取订阅的站点，已订阅 + 推荐 - 取消订阅
    :param sub_feeds:
    :param unsub_feeds:
    :return:
    """
    recommend_feeds = list(Site.objects.filter(status='active', star__gte=20).values_list('name', flat=True))
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
    return R.get(settings.REDIS_VISIT_KEY % (current_day(), uid))


def set_visit_today(uid):
    return R.set(settings.REDIS_VISIT_KEY % (current_day(), uid), 1, 24*3600+100)


def is_old_user(uid):
    """
    是否是老用户（过去一周）
    :param uid:
    :return:
    """
    return R.get(settings.REDIS_WEEK_KEY % uid)


def set_old_user(uid):
    return R.set(settings.REDIS_WEEK_KEY % uid, 1, 7*24*3600)


def incr_redis_key(key):
    return R.incr(key, amount=1)


def add_refer_host(host):
    return R.sadd(settings.REDIS_REFER_ALL_KEY, host)
