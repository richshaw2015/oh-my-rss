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
from web.utils import R, get_content_from_dat, is_user_stared

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


@register.filter
@lru_cache(maxsize=1024)
def to_short_author(author1, author2=''):
    """
    作者显示名称，最多 6 个汉字
    """
    author = author1 if author1 else author2

    if not author:
        author = 'None'

    return cut_to_short(author, 12)


@register.filter
@lru_cache(maxsize=1024)
def to_short_site_name(name):
    """
    订阅源显示名称，最多 10 个汉字
    """
    return cut_to_short(name, 20)


@register.filter
@lru_cache(maxsize=1024)
def to_clean_brief(brief):
    """
    去掉第三方说明性的文字
    """
    return re.sub(r' - Made with love by .*$', '', brief)[:50]


@register.filter
@lru_cache(maxsize=1024)
def to_article_content(uindex, content):
    if content.strip():
        return content
    else:
        return get_content_from_dat(uindex)


@register.filter
@lru_cache(maxsize=512)
def to_rss(site):
    if site.creator == 'user':
        rss = site.rss
    else:
        rss = reverse('get_feed_entries', kwargs={"site_id": site.pk})

    if not rss:
        logger.error(f'生成 RSS 失败：`{site.pk}`{site.creator}')

    return rss


@register.filter
def to_site_update_count(site_id):
    key = settings.REDIS_SITE_ARTICLES_KEY % site_id
    return R.scard(key)
