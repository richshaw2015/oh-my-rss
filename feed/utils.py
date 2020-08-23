# -*- coding: utf-8 -*-

import os
import redis
from ohmyrss.settings import REDIS_FEED_DB, REDIS_HOST, REDIS_PORT, CRAWL_FLAG_DIR
import time
import urllib
import hashlib


R = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_FEED_DB, decode_responses=True)
CRAWL_PREFIX = 'CRAWL/'


def mkdir(directory):
    return os.makedirs(directory, exist_ok=True)


def get_hash_name(s):
    return hashlib.md5(s.encode('utf8')).hexdigest()


def is_crawled_url(url):
    url_hash = get_hash_name(url)
    flag_dir = os.path.join(CRAWL_FLAG_DIR, url_hash[0], url_hash[-1])
    flag_file = os.path.join(flag_dir, url_hash)

    return os.path.exists(flag_file)


def mark_crawled_url(*urls):
    # 跳转前后要设置；有些有中文路径的需要还原
    for url in urls:
        write_crawl_flag_file(url)

        if url != urllib.parse.unquote(url):
            write_crawl_flag_file(urllib.parse.unquote(url))

    return True


def write_crawl_flag_file(url):
    url_hash = get_hash_name(url)
    flag_dir = os.path.join(CRAWL_FLAG_DIR, url_hash[0], url_hash[-1])

    mkdir(flag_dir)
    flag_file = os.path.join(flag_dir, url_hash)

    if os.path.exists(flag_file):
        return True

    try:
        open(flag_file, 'w').close()
    except:
        return False

    return True


def current_ts():
    return int(time.time() * 1000)
