from django import template
from django.utils.timezone import localtime
from django.conf import settings
from django.urls import reverse
import hashlib
import urllib
import logging
from functools import lru_cache

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
    dt = localtime(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


@register.filter
def to_view_uv(uv_dict, uindex):
    """
    to user visit data
    :param uv_dict:
    :param uindex:
    :return:
    """
    return uv_dict.get(settings.REDIS_VIEW_KEY % uindex) or 0


@register.filter
def to_thumb_uv(uv_dict, uindex):
    """
    to thumb data
    :param uv_dict:
    :param uindex:
    :return:
    """
    return uv_dict.get(settings.REDIS_THUMB_KEY % uindex) or 0


@register.filter
def to_open_uv(uv_dict, uindex):
    """
    to open count data
    :param uv_dict:
    :param uindex:
    :return:
    """
    return uv_dict.get(settings.REDIS_OPEN_KEY % uindex) or 0


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


def cut_to_short(text, size):
    """
    剪切指定的显示字符数；英文字符占1个显示宽度，中文占2个显示宽度
    :param text:
    :param size:
    :return:
    """
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

    return cut_to_short(author, 12)


@register.filter
@lru_cache(maxsize=1024)
def to_short_site_name(name):
    """
    订阅源显示名称，最多 10 个汉字
    """
    return cut_to_short(name, 20)


@register.filter
@lru_cache(maxsize=512)
def to_rss(site):
    if site.creator == 'user':
        rss = site.rss
    else:
        rss = reverse('get_feed_entries', kwargs={"name": site.name})

    if not rss:
        logger.error(f'生成 RSS 失败：`{site.name}`{site.creator}')

    return rss
