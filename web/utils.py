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
import re
from web.stopwords import stopwords
import jieba
from whoosh.fields import Schema, TEXT, ID
from feed.utils import mkdir, get_hash_name
from bs4 import BeautifulSoup

# init Redis connection
R = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_WEB_DB, decode_responses=True)
logger = logging.getLogger(__name__)

if not settings.DEBUG:
    # init jieba
    jieba.initialize()

UAS = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/74.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/13.0 Safari/534.50',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Win64; x64; Trident/5.0)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36',
]


def get_host_name(url):
    return urlparse(url).netloc


def get_short_host_name(url):
    host = urlparse(url).netloc
    return re.sub(r'^www\.|^blog.', '', host)


def get_random_ua():
    return random.choice(UAS)


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


@lru_cache(maxsize=4)
def get_profile_apis():
    return (
        reverse('get_article_update_view'), reverse('get_lastweek_articles'), reverse('get_recent_articles'),
        reverse('get_site_update_view'), reverse('get_site_article_update_view'), reverse('in_site_search')
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
def get_visitor_subscribe_feeds(sub_feeds, unsub_feeds, star=25):
    """
    获取游客订阅的站点；已订阅 + 推荐 - 取消订阅；最多返回 50 个
    """
    # 设置订阅源缓存
    set_active_rss(sub_feeds)

    # TODO 优化这里的性能
    recommend_feeds = list(Site.objects.filter(status='active', star__gte=star).values_list('id', flat=True))
    active_feeds = {int(s) for s in get_active_sites()}

    try:
        return list((set(list(sub_feeds) + recommend_feeds) - set(unsub_feeds)) & active_feeds
                    )[:settings.VISITOR_SUBS_LIMIT]
    except:
        return []


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def current_day():
    return time.strftime("%Y%m%d", time.localtime(time.time()))


def get_xaxis_days(days=60):
    """
    获取 X 坐标，按天。取两个月数据
    """
    xaxis_days = []

    for i in range(0, days):
        xaxis_days.append(time.strftime("%Y%m%d", time.localtime(time.time() - i * 86400)))

    xaxis_days.sort()
    return xaxis_days


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


def add_referer_day_host(host):
    key = settings.REDIS_REFER_DAY_KEY % current_day()

    return R.sadd(key, host)


def add_referer_stats(referer):
    if referer:
        host = get_host_name(referer)

        if host and host not in settings.ALLOWED_HOSTS:
            logger.info(f"收到外域来源：`{host}`{referer}")

            add_referer_day_host(host)
            incr_redis_key(settings.REDIS_REFER_PV_DAY_KEY % (host, current_day()))


def reset_recent_articles(articles):
    key = settings.REDIS_ARTICLES_KEY

    R.delete(key)

    R.sadd(key, *articles)

    R.expire(key, 600)

    return True


def get_recent_articles():
    key = settings.REDIS_ARTICLES_KEY
    return R.smembers(key)


def reset_recent_site_articles(site_id, articles):
    key = settings.REDIS_SITE_ARTICLES_KEY % site_id

    R.delete(key)

    R.sadd(key, *articles)

    R.expire(key, 600)

    return True


def get_recent_site_articles(site_id):
    key = settings.REDIS_SITE_ARTICLES_KEY % site_id
    return R.smembers(key)


def set_site_lastid(site_id, uindex):
    key = settings.REDIS_SITE_LASTID_KEY % site_id
    return R.set(key, uindex, 600)


def get_site_last_id(site_id):
    key = settings.REDIS_SITE_LASTID_KEY % site_id
    return R.get(key) or '0'


def reset_sites_lastids(ids):
    key = settings.REDIS_SITES_LASTIDS_KEY
    R.delete(key)
    return R.sadd(key, *ids)


def get_sites_lastids():
    key = settings.REDIS_SITES_LASTIDS_KEY
    return sorted(R.smembers(key), reverse=True)


def add_user_sub_feeds(oauth_id, feeds):
    key = settings.REDIS_USER_SUB_KEY % oauth_id

    return R.sadd(key, *feeds)


def del_user_sub_feed(oauth_id, feed):
    key = settings.REDIS_USER_SUB_KEY % oauth_id

    return R.srem(key, feed)


def set_active_sites(sites):
    """
    批量设置有效的源（未下线的）
    """
    key = settings.REDIS_ACTIVE_SITES_KEY
    R.delete(key)
    return R.sadd(key, *sites)


def set_active_site(site):
    """
    设置单个源有效（未下线的）
    """
    key = settings.REDIS_ACTIVE_SITES_KEY
    return R.sadd(key, site)


def get_active_sites():
    key = settings.REDIS_ACTIVE_SITES_KEY
    return R.smembers(key)


def get_user_subscribe_feeds(oauth_id, from_user=True, user_level=1):
    """
    获取登陆用户订阅源
    """
    key = settings.REDIS_USER_SUB_KEY % oauth_id

    sub_feeds = R.smembers(key) & get_active_sites()

    # 普通用户，限制其订阅数量
    if user_level < 10:
        sub_feeds = list(sub_feeds)[:settings.USER_SUBS_LIMIT]

    # 设置订阅源缓存，来自用户的请求调用
    if from_user:
        set_active_rss(sub_feeds)

        if not sub_feeds:
            logger.warning(f'用户未订阅任何内容：`{oauth_id}')

    return [int(i) for i in sub_feeds]


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
    :return:
    """
    if articles:
        user_read_keys = [settings.REDIS_USER_READ_KEY % (oauth_id, uindex) for uindex in articles]
        return len(articles) - R.mget(*user_read_keys).count('1')
    else:
        return 0


def get_user_unread_articles(oauth_id, articles):
    """
    计算用户未读的文章
    """
    unread_articles = set()

    for uindex in articles:
        key = settings.REDIS_USER_READ_KEY % (oauth_id, uindex)

        if R.get(key) != '1':
            unread_articles.add(uindex)

    return unread_articles


def get_user_unread_sites(oauth_id, sites):
    """
    计算未读的站点
    """
    unread_sites = set()

    for site_id in sites:
        site_articles = get_recent_site_articles(site_id)
        if get_user_unread_count(oauth_id, site_articles) > 0:
            unread_sites.add(site_id)

    return unread_sites


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


def get_user_visit_days(oauth_id):
    """
    计算一个用户登陆的天数（过去一个月）
    """
    user_visit_keys = [settings.REDIS_USER_VISIT_DAY_KEY % (oauth_id, day) for day in get_xaxis_days(31)]
    return R.mget(*user_visit_keys).count('1')


def set_user_ranking_list(ranking):
    return R.set(settings.REDIS_USER_RANKING_KEY, json.dumps(ranking))


def get_user_ranking_list():
    return json.loads(R.get(settings.REDIS_USER_RANKING_KEY))


def save_avatar(avatar, userid, size=100, referer=None):
    """
    保存网络头像
    :param avatar:
    :param userid:
    :param size:
    :param referer:
    :return: 保存后的头像地址
    """
    try:
        headers = {'Referer': referer} if referer else {}

        rsp = requests.get(avatar, timeout=15, headers=headers)

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
    计算两个列表的余弦相似度，0 ~ 1 TODO 目前无用
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


def set_indexed(tag, key):
    key = settings.REDIS_INDEXED_KEY % (tag, key)
    return R.set(key, '1', 30*86400)


def is_indexed(tag, key):
    key = settings.REDIS_INDEXED_KEY % (tag, key)
    return R.get(key) == '1'


def set_job_dvcs(dvcs):
    key = settings.REDIS_JOB_DVC_KEY
    return R.sadd(key, *dvcs)


def set_job_stat(stat):
    key = settings.REDIS_JOB_STAT_KEY % (current_day(), stat.dvc_id, stat.status)
    return R.set(key, stat.c, 30*24*3600)


def set_updated_site(site_id, ttl=2*3600):
    """
    设置站点更新标记，2 小时
    """
    key = settings.REDIS_UPDATED_SITE_KEY % site_id
    return R.set(key, '1', ttl)


def is_updated_site(site_id):
    key = settings.REDIS_UPDATED_SITE_KEY % site_id
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


def del_dat2_file(uindex, site_id):
    file = os.path.join(settings.HTML_DATA2_DIR, str(site_id), f"{uindex}.html")
    try:
        os.remove(file)
        return True
    except:
        pass

    return False


def write_dat2_file(uindex, site_id, content):
    """
    写入到文件系统；写入成功或已经存在返回 True
    """
    new_dir = os.path.join(settings.HTML_DATA2_DIR, str(site_id))
    mkdir(new_dir)

    file = os.path.join(new_dir, f"{uindex}.html")

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


@lru_cache(maxsize=2048)
def get_content(uindex, site_id):
    file = os.path.join(os.path.join(settings.HTML_DATA2_DIR, str(site_id)), f"{uindex}.html")

    if os.path.exists(file):
        return open(file, encoding='UTF8').read()
    else:
        logger.warning(f"文件丢失：`{file}")

    return ''


def get_random_emoji():
    pics = os.listdir(os.path.join(settings.BASE_DIR, 'assets', 'emoji'))
    pics = [pic for pic in pics if pic.endswith('.png')]

    return '/assets/emoji/' + random.choice(pics)


def generate_rss_avatar(link, feed=''):
    """
    生成用户提交 RSS 源的默认头像
    :param link:
    :param feed:
    :return:
    """
    avatar, link_host, feed_host = "", get_host_name(link), get_host_name(feed)

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
    elif settings.CHUANSONGME_HOST in link_host:
        avatar = '/assets/img/chuansongme.jpg'
    elif 'ximalaya.com' in link_host:
        avatar = '/assets/img/ximalaya.png'
    elif 'smzdm.com' in link_host:
        avatar = '/assets/img/smzdm.jpg'
    elif settings.QNMLGB_HOST in link_host:
        avatar = '/assets/img/qnmlgb.png'
    elif link_host == 'weixin.sogou.com':
        avatar = '/assets/img/sogou.png'
    elif link_host == 'pubs.acs.org':
        avatar = '/assets/img/acs.jpg'
    elif 'vreadtech.com' in link_host:
        avatar = '/assets/img/vtechread.jpg'
    elif 'news.qq.com' in link_host:
        avatar = '/assets/img/qqcom.png'
    elif 'werss.app' in link_host:
        avatar = '/assets/img/werss.png'
    # 其次根据 feed 地址匹配
    elif 'feed43.com' in feed_host:
        avatar = '/assets/img/feed43.png'

    # 随机匹配一个 emoji
    if not avatar:
        avatar = get_random_emoji()

    return avatar


@lru_cache(maxsize=1024)
def is_sensitive_content(uindex, site_id):
    """
    文章是否命中国内的敏感词
    """
    is_sensitive, content = False, get_content(uindex, site_id)

    for word in settings.SENSITIVE_WORDS:
        if word in content:
            is_sensitive = True
            break

    return is_sensitive


def get_with_retry(url):
    """
    普通爬取。重试 2 次
    :param url:
    :return:
    """
    for i in range(0, 2):
        headers = {'User-Agent': get_random_ua()}

        try:
            return requests.get(url, verify=False, timeout=30, headers=headers)
        except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
            logger.warning(f"请求出现网络异常：`{url}")
        except:
            logger.warning(f"请求出现未知异常：`{url}")

        time.sleep(20)

    return None


def set_user_site_cname(oauth_id, site_id, site_name):
    key = settings.REDIS_USER_CONF_SITE_NAME_KEY % (oauth_id, site_id)
    return R.set(key, site_name)


def get_user_site_cname(oauth_id, site_id):
    key = settings.REDIS_USER_CONF_SITE_NAME_KEY % (oauth_id, site_id)
    return R.get(key)


def set_user_site_author(oauth_id, site_id, site_author):
    key = settings.REDIS_USER_CONF_SITE_AUTHOR_KEY % (oauth_id, site_id)
    return R.set(key, site_author)


def get_user_site_author(oauth_id, site_id):
    key = settings.REDIS_USER_CONF_SITE_AUTHOR_KEY % (oauth_id, site_id)
    return R.get(key)


def valid_dvc_req(dvc_id, dvc_type, sign):
    src = dvc_id + dvc_type + current_day()
    return get_hash_name(src) == sign


def get_html_text(html):
    bs = BeautifulSoup(html, "html.parser")
    return bs.get_text()


@lru_cache(maxsize=128)
def split_cn_words(cn, join=False):
    """
    中文分词；停词不计算
    """
    seg_list, word_list = jieba.cut(cn), []

    for seg in seg_list:
        seg = seg.strip().lower()

        if seg and seg not in stopwords:
            word_list.append(seg)

    if join:
        return ','.join(word_list)

    return word_list


def is_podcast_feed(feed_obj):
    try:
        return 'podcast' in feed_obj.namespaces.get('itunes', '')
    except AttributeError:
        pass

    return False


def trim_brief(brief):
    """
    去掉第三方说明性的文字
    """
    brief = re.sub(r' - Made with love by .*$', '', brief)
    return re.sub(r'\(RSS provided by .*$', '', brief).strip()


def to_podcast_duration(duration):
    dest = duration

    try:
        if ':' not in duration:
            seconds = int(duration)

            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            if h > 0:
                return "%02d:%02d:%02d" % (h, m, s)
            else:
                return "%02d:%02d" % (m, s)
    except ValueError:
        logger.warning(f"转换时间失败：`{duration}")

    return dest


# 搜索对象
whoosh_site_schema = Schema(
    id=ID(stored=True, unique=True),

    cname=TEXT(field_boost=5.0),
    author=TEXT(field_boost=3.0),
    brief=TEXT(),
)
whoosh_article_schema = Schema(
    uindex=ID(stored=True, unique=True),

    title=TEXT(field_boost=5.0),
    author=TEXT(field_boost=3.0),
    content=TEXT(),
)
