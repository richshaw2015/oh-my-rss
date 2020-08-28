from django import template
from django.utils.timezone import localtime
from django.conf import settings
from django.urls import reverse
import hashlib
import urllib
import logging
from functools import lru_cache
import re
import time
from web.utils import R, get_content, is_user_stared, get_user_site_cname, get_user_site_author

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def to_stars(num):
    """
    turn feed score to stars
    :param num:
    :return:
    """
    return '★' * int(num / 10)


@register.filter
def to_date_fmt(dt):
    """
    to "YYYY-MM-DD hh:mm:ss" format
    :param dt:
    :return:
    """
    if isinstance(dt, str):
        if len(dt) == 13:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(dt[:10])))
        elif dt == '0':
            return ''
        else:
            return dt[:19]
    else:
        dt = localtime(dt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


@register.filter
def to_view_uv(uindex):
    return R.get(settings.REDIS_VIEW_KEY % uindex) or 0


@register.filter
def to_star_uv(uindex):
    return R.get(settings.REDIS_STAR_KEY % uindex) or 0


@register.filter
def to_fuzzy_uid(uid):
    return uid[:3] + '**' + uid[-3:]


@register.filter
def to_gravatar_url(uid, size=64):
    return "https://cdn.v2ex.com/gravatar/%s?d=retro&s=%d" % (hashlib.md5(uid.lower().encode('utf8')).hexdigest(),
                                                                 size)


@register.filter
def unquote(url):
    return urllib.parse.unquote(url)


@register.filter
def is_user_read_article(user_id, uindex):
    """
    :param user_id:
    :param uindex:
    :return:
    """
    key = settings.REDIS_USER_READ_KEY % (user_id, uindex)
    return R.get(key) == '1'


@register.filter
def is_user_stared_article(user_id, uindex):
    return is_user_stared(user_id, uindex)


def cut_to_short(text, size):
    """
    剪切指定的显示字符数；英文字符占1个显示宽度，中文占2个显示宽度
    :param text:
    :param size:
    :return:
    """
    if not text:
        return ''

    display_len = 0
    short = ''

    for char in text[:size]:
        if len(char.encode('utf8')) > 1:
            display_len += 2
        else:
            display_len += 1

        if display_len <= size:
            short += char
        else:
            break
    return short


@register.simple_tag
def to_short_author(user, **kwargs):
    if user:
        author = get_user_site_author(user.oauth_id, kwargs.get('s'))

        if author:
            return cut_to_short(author, 12)

    author = kwargs.get('a1') or kwargs.get('a2') or 'None'

    return cut_to_short(author, 12)


@register.filter
def to_short_site_cname(user, site):
    """
    订阅源显示名称，最多 10 个汉字，支持用户自定义名称
    """
    if isinstance(site, dict):
        site_id = site['id']
        site_cname = site['cname']
    else:
        site_id = site.id
        site_cname = site.cname

    if user:
        cname = get_user_site_cname(user.oauth_id, site_id)
        if cname:
            return cut_to_short(cname, 20)

    return cut_to_short(site_cname, 20)


@register.filter
def to_site_cname(user, site):
    """
    订阅源显示名称，支持用户自定义名称
    """
    if isinstance(site, dict):
        site_id = site['id']
        site_cname = site['cname']
    else:
        site_id = site.id
        site_cname = site.cname

    if user:
        cname = get_user_site_cname(user.oauth_id, site_id)
        if cname:
            return cname

    return site_cname


@register.filter
@lru_cache(maxsize=1024)
def to_article_content(uindex, site_id):
    return get_content(uindex, site_id)


@register.filter
@lru_cache(maxsize=512)
def to_rss(site):
    if site.creator in ('system', 'wemp'):
        rss = reverse('get_feed_entries', kwargs={"site_id": site.pk})
    else:
        rss = site.rss

    if not rss:
        logger.error(f'生成 RSS 失败：`{site.pk}`{site.creator}')

    return rss


@register.filter
def to_site_update_count(site_id):
    key = settings.REDIS_SITE_ARTICLES_KEY % site_id
    return R.scard(key)
