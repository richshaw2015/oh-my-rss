# -*- coding: utf-8 -*-

import os
import redis
from ohmyrss.settings import REDIS_FEEDS_DB, REDIS_HOST, REDIS_PORT
import urllib
import time


R = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_FEEDS_DB, decode_responses=True)
CRAWL_PREFIX = 'CRAWL/'


def mkdir(directory):
    """
    :param directory: 建立目录，不管是否存在
    :return:
    """
    return os.makedirs(directory, exist_ok=True)


def is_crawled_url(url):
    """
    地址已经被抓取过
    :param url:
    :return:
    """
    if R.get(CRAWL_PREFIX + url):
        return True
    return False


def set_crawled_url(url):
    """
    设置已经被抓取过
    :param url:
    :return:
    """
    if not R.set(CRAWL_PREFIX + url, 1):
        # TODO 增加异常日志处理
        pass


def current_ts():
    return int(time.time() * 1000)
