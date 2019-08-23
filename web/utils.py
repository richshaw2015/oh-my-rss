# -*- coding: utf-8 -*-

import os
import redis
from django.conf import settings
from .models import Site
import logging

# init Redis connection
R = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_WEB_DB, decode_responses=True)
logger = logging.getLogger(__name__)


def incr_redis_key(action, uindex):
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


def get_subscribe_sites(sub_feeds, unsub_feeds):
    """
    获取订阅的站点，已订阅 + 推荐 - 取消订阅
    TODO 增加缓存处理
    :param sub_feeds:
    :param unsub_feeds:
    :return:
    """
    recommend_feeds = list(Site.objects.filter(status='active', star__gte=20).values_list('name', flat=True))
    return list(set(sub_feeds + recommend_feeds) - set(unsub_feeds))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
