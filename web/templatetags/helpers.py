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


@register.filter
@lru_cache(maxsize=1024)
def to_short_author(author1, author2=''):
    """
    max 12 chars and 6 chinese chars
    :param author1:
    :param author2:
    :return:
    """
    author = author1 if author1 else author2

    display_len = 0
    short_author = ''

    if author:
        for char in author[:12]:
            if len(char.encode('utf8')) > 1:
                display_len += 2
            else:
                display_len += 1

            if display_len <= 12:
                short_author += char
            else:
                break

    return short_author


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
