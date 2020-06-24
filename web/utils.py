# -*- coding: utf-8 -*-

import time
import random

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
from collections import Counter
from urllib.parse import urlparse
import json
from fake_useragent import UserAgent
import django_rq

# init Redis connection
R = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_WEB_DB, decode_responses=True)
logger = logging.getLogger(__name__)


def get_host_name(url):
    return urlparse(url).netloc


def incr_view_star(action, uindex):
    """
    文章浏览数、收藏数统计，保留一年数据
    :param action:
    :param uindex:
    :return:
    """
    key = None

    if action == 'VIEW':
        key = settings.REDIS_VIEW_KEY % uindex
    elif action == 'STAR':
        key = settings.REDIS_STAR_KEY % uindex

    if key is not None:
        ret = R.incr(key)

        if ret == 1:
            R.expire(key, 365 * 86400)

        return ret

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
        key_list.extend([settings.REDIS_VIEW_KEY % article.uindex, settings.REDIS_STAR_KEY % article.uindex])

    data_list = R.mget(*key_list)

    return dict(zip(key_list, data_list))


@lru_cache(maxsize=4)
def get_profile_apis():
    return (
        reverse('get_article_update_view'), reverse('get_lastweek_articles'), reverse('get_recent_articles'),
        reverse('get_site_update_view'), reverse('get_site_article_update_view'),
    )


def set_active_rss(feeds):
    """
    访问过的源，设置一个标识，3天缓存
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
def get_subscribe_feeds(sub_feeds, unsub_feeds, star=25):
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

    return R.get(key) == '1'


def set_visit_today(uid):
    key = settings.REDIS_VISIT_KEY % (current_day(), uid)

    return R.set(key, 1, 24*3600+100)


def is_old_user(uid):
    """
    是否是老用户（过去一周）
    :param uid:
    :return:
    """
    key = settings.REDIS_WEEK_KEY % uid

    return R.get(key) == '1'


def set_old_user(uid):
    key = settings.REDIS_WEEK_KEY % uid

    return R.set(key, 1, 7*24*3600)


def incr_redis_key(key):
    return R.incr(key, amount=1)


def add_referer_host(host):
    key = settings.REDIS_REFER_ALL_KEY

    return R.sadd(key, host)


def add_referer_stats(referer):
    if referer:
        host = get_host_name(referer)

        if host and host not in settings.ALLOWED_HOSTS:
            logger.info(f"收到外域来源：`{host}`{referer}")

            add_referer_host(host)
            incr_redis_key(settings.REDIS_REFER_PV_KEY % host)
            incr_redis_key(settings.REDIS_REFER_PV_DAY_KEY % (host, current_day()))


def add_user_sub_feeds(oauth_id, feeds):
    key = settings.REDIS_USER_SUB_KEY % oauth_id

    return R.sadd(key, *feeds)


def del_user_sub_feed(oauth_id, feed):
    key = settings.REDIS_USER_SUB_KEY % oauth_id

    return R.srem(key, feed)


def get_user_sub_feeds(oauth_id, from_user=True):
    key = settings.REDIS_USER_SUB_KEY % oauth_id

    sub_feeds = R.smembers(key)

    # 设置订阅源缓存，来自用户的请求调用
    if from_user:
        set_active_rss(sub_feeds)

        if not sub_feeds:
            logger.warning(f'用户未订阅任何内容：`{oauth_id}')

    return sub_feeds


def set_proxy_ips(proxies):
    R.delete(settings.REDIS_PROXY_KEY)
    return R.sadd(settings.REDIS_PROXY_KEY, *proxies)


def del_proxy_ip(proxy):
    return R.srem(settings.REDIS_PROXY_KEY, proxy)


def get_one_proxy_ip():
    """
    返回一个 IP，同时返回 IP 池数量
    """
    proxies = tuple(R.smembers(settings.REDIS_PROXY_KEY))

    if len(proxies) == 0:
        return None, 0
    else:
        return random.choice(proxies), len(proxies)


def set_user_read_article(oauth_id, uindex):
    """
    已登录用户同步已读文章状态
    """
    key = settings.REDIS_USER_READ_KEY % (oauth_id, uindex)

    return R.set(key, 1, 30*24*3600)


def set_user_read_articles(oauth_id, ids):
    """
    已登录用户同步已读文章状态
    :param oauth_id:
    :param ids:
    :return:
    """
    with R.pipeline(transaction=False) as p:
        for uindex in ids:
            key = settings.REDIS_USER_READ_KEY % (oauth_id, uindex)
            p.set(key, 1, 14*24*3600)
        p.execute()


def get_user_unread_count(oauth_id, articles):
    """
    计算用户对一批文章的未读数
    :param oauth_id:
    :param articles:
    :return:
    """
    user_read_keys = [settings.REDIS_USER_READ_KEY % (oauth_id, uindex) for uindex in articles]
    return len(articles) - R.mget(*user_read_keys).count('1')


def get_login_user(request):
    """
    获取已登录用户信息
    :param request:
    :return: 获取成功返回 User 对象；用户不存在则返回 None
    """
    oauth_id = request.get_signed_cookie('oauth_id', False)
    # if settings.DEBUG:
    #     oauth_id = 'github/28855629'

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

    return '/assets/img/logo.svg'


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

    return R.hgetall(key)


def set_similar_article(uindex, simlar_dict):
    key = settings.REDIS_SIMILAR_ARTICLE_KEY % uindex

    ret = R.hmset(key, simlar_dict)
    R.expire(key, 30 * 24 * 3600)
    return ret


def set_user_visit_day(oauth_id):
    key = settings.REDIS_USER_VISIT_DAY_KEY % (oauth_id, current_day())

    return R.set(key, '1', 30 * 24 * 3600)


def set_feed_ranking_dict(ranking_dict):
    key = settings.REDIS_FEED_RANKING_KEY

    return R.set(key, json.dumps(ranking_dict))


def get_feed_ranking_dict():
    key = settings.REDIS_FEED_RANKING_KEY
    try:
        return json.loads(R.get(key))
    except:
        logger.error(f"读取 Redis 出现异常：`{key}")

    return {}


def set_updated_site(site_name, ttl=2*3600):
    """
    设置站点更新标记，2 小时
    """
    key = settings.REDIS_UPDATED_SITE_KEY % site_name
    return R.set(key, '1', ttl)


def is_updated_site(site_name):
    key = settings.REDIS_UPDATED_SITE_KEY % site_name
    return R.get(key) == '1'


def set_user_stared(oauth_id, uindex):
    """
    设置用户收藏，保存一年时间
    """
    key = settings.REDIS_USER_STAR_KEY % (oauth_id, uindex)

    return R.set(key, '1', 365 * 24 * 3600)


def is_user_stared(oauth_id, uindex):
    """
    用户是否收藏
    """
    key = settings.REDIS_USER_STAR_KEY % (oauth_id, uindex)

    return R.get(key) == '1'


def write_dat_file(uindex, content):
    """
    写入到文件系统；写入成功或已经存在返回 True
    """
    file = os.path.join(settings.HTML_DATA_DIR, str(uindex))

    if os.path.exists(file):
        return True

    try:
        if content.strip():
            with open(file, 'w', encoding='UTF8') as f:
                f.write(content)
            return True
    except:
        logger.warning(f"写入文件失败：`{uindex}")

    return False


def get_content_from_dat(uindex):
    file = os.path.join(settings.HTML_DATA_DIR, str(uindex))

    if os.path.exists(file):
        return open(file, encoding='UTF8').read()

    return ''


def generate_rss_avatar(link, feed=''):
    """
    生成用户提交 RSS 源的默认头像
    :param link:
    :param feed:
    :return:
    """
    avatar = "/assets/img/logo.svg"
    link_host = get_host_name(link)
    feed_host = get_host_name(feed)

    # 首先根据 link 地址匹配
    if 'weibo.com' in link_host or 'weibo.cn' in link_host:
        avatar = "/assets/img/weibo.jpg"
    elif "jianshu.com" in link_host:
        avatar = "/assets/img/jianshu.png"
    elif link_host in ('blog.sina.com', 'blog.sina.com.cn'):
        avatar = '/assets/img/blogsina.jpg'
    elif 'sina.com.cn' in link_host:
        avatar = '/assets/img/sinanews.png'
    elif 'twitter.com' in link_host:
        avatar = '/assets/img/twitter.png'
    elif 'youtube.com' in link_host:
        avatar = '/assets/img/youtube.png'
    elif link_host == 'music.163.com':
        avatar = '/assets/img/163music.jpg'
    elif 'douban.com' in link_host:
        avatar = '/assets/img/douban.png'
    elif 'zhihu.com' in link_host:
        avatar = '/assets/img/zhihu.png'
    elif 'bilibili.com' in link_host:
        avatar = '/assets/img/bilibili.png'
    elif link_host == 'xueqiu.com':
        avatar = '/assets/img/xueqiu.jpg'
    elif 'tophub.today' in link_host:
        avatar = '/assets/img/tophub.png'
    elif 'github.com' in link_host:
        avatar = '/assets/img/github.png'
    elif 'juejin.im' in link_host:
        avatar = '/assets/img/juejin.png'
    elif 'rsshub.app' in link_host:
        avatar = '/assets/img/rsshub.png'
    elif 'chuansongme.com' in link_host:
        avatar = '/assets/img/chuansongme.jpg'
    elif 'ximalaya.com' in link_host:
        avatar = '/assets/img/ximalaya.png'
    elif 'smzdm.com' in link_host:
        avatar = '/assets/img/smzdm.jpg'
    elif link_host == "qnmlgb.tech":
        avatar = '/assets/img/qnmlgb.png'
    elif link_host == 'weixin.sogou.com':
        avatar = '/assets/img/sogou.png'
    elif link_host == 'pubs.acs.org':
        avatar = '/assets/img/acs.jpg'
    elif 'vreadtech.com' in link_host:
        avatar = '/assets/img/vtechread.jpg'
    elif 'news.qq.com' in link_host:
        avatar = '/assets/img/qqcom.png'
    # 其次根据 feed 地址匹配
    elif 'feed43.com' in feed_host:
        avatar = '/assets/img/feed43.png'

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


def is_sensitive_content(uindex, content):
    """
    文章是否命中国内的敏感词
    """
    is_sensitive = False

    if not content.strip():
        content = get_content_from_dat(uindex)

    for word in settings.SENSITIVE_WORDS:
        if word in content:
            is_sensitive = True
            break

    return is_sensitive

#
# def get_with_proxy(url):
#     """
#     通过 代理 请求，重试 3 次
#     :param url:
#     :return:
#     """
#     for i in range(0, 3):
#         proxy_ip_port, proxy_pool = get_one_proxy_ip()
#
#         if proxy_pool <= 10:
#             logger.warning("代理 IP 池不够 10 个了，开始异步更新")
#             from web.tasks import update_proxy_pool_cron
#             django_rq.enqueue(update_proxy_pool_cron)
#
#         if proxy_ip_port is not None:
#             proxy = {"http": proxy_ip_port, "https": proxy_ip_port}
#             header = {'User-Agent': UserAgent().random}
#
#             try:
#                 rsp = requests.get(url, verify=False, timeout=15, headers=header, proxies=proxy)
#                 logger.info(f"代理请求成功：`{url}`{proxy_ip_port}")
#                 return rsp
#             except requests.exceptions.ProxyError:
#                 del_proxy_ip(proxy_ip_port)
#             except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
#                 logger.warning(f"代理请求出现网络异常：`{url}`{proxy}")
#             except:
#                 logger.warning(f"代理请求出现未知异常：`{url}`{proxy}")
#         else:
#             # 等待代理 IP 池更新
#             time.sleep(10)
#     return None


def get_with_proxy(url):
    """
    先不使用代理，免费的不靠谱；待后续改造
    :param url:
    :return:
    """
    header = {'User-Agent': UserAgent().random}

    try:
        return requests.get(url, verify=False, timeout=15, headers=header)
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        logger.warning(f"GET 请求出现网络异常：`{url}")
    except:
        logger.warning(f"GET 请求出现未知异常：`{url}")

    return None


def get_with_retry(url):
    """
    普通爬取。重试 2 次
    :param url:
    :return:
    """
    for i in range(0, 2):
        header = {'User-Agent': UserAgent().random}

        try:
            return requests.get(url, verify=False, timeout=30, headers=header)
        except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
            logger.warning(f"请求出现网络异常：`{url}")
        except:
            logger.warning(f"请求出现未知异常：`{url}")

        time.sleep(20)

    return None


def guard_log(msg, hits=3, duration=86400):
    """
    哨兵日志，满足 duration hits 条件才打印
    :param msg:
    :param hits:
    :param duration:
    :return:
    """
    logger.info(msg)

    log_key = f"LOG/{msg}"

    count = R.incr(log_key)

    if count == 1:
        R.expire(log_key, duration)

    if count >= hits:
        logger.warning(msg)
