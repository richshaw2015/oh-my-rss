# -*- coding: utf-8 -*-

import os
import redis
from django.conf import settings
import logging

# 初始化一个全局的 Redis 连接
R = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_API_DB, decode_responses=True)


def incr_redis_key(action, uindex):
    """
    执行加1操作
    :param key:
    :param uindex:
    :return:
    """
    key = None
    if action == 'VIEW':
        key = settings.REDIS_VIEW_KEY % uindex
    elif action == 'LIKE':
        key = settings.REDIS_LIKE_KEY % uindex
    elif action == 'ADDGP':
        key = settings.REDIS_ADDGP_KEY % uindex

    if key is not None:
        try:
            return R.incr(key, amount=1)
        except ConnectionError:
            logging.warning(f"写入Redis出现异常：{key}")
    return False


def get_page_uv(page):
    """
    获取页面上所有文章的UV数、点赞数、加群数
    :param page:
    :return:
    """
    key_list = []
    for article in page.object_list:
        key_list.extend([settings.REDIS_VIEW_KEY % article.uindex, settings.REDIS_LIKE_KEY % article.uindex,
                         settings.REDIS_ADDGP_KEY % article.uindex])
    data_list = R.mget(*key_list)
    return dict(zip(key_list, data_list))
