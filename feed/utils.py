# -*- coding: utf-8 -*-

import os
import redis
from ohmyrss.settings import REDIS_FEED_DB, REDIS_HOST, REDIS_PORT
import time
import urllib


R = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_FEED_DB, decode_responses=True)
CRAWL_PREFIX = 'CRAWL/'


def mkdir(directory):
    return os.makedirs(directory, exist_ok=True)


def is_crawled_url(url):
    return R.get(CRAWL_PREFIX + url) == '1'


def mark_crawled_url(*urls):
    # 跳转前后要设置；有些有中文路径的需要还原
    for url in urls:
        R.set(CRAWL_PREFIX + url, 1, ex=12 * 30 * 86400)
        R.set(CRAWL_PREFIX + urllib.parse.unquote(url), 1, ex=12 * 30 * 86400)


def current_ts():
    return int(time.time() * 1000)
