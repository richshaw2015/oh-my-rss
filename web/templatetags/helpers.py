from django import template
from django.utils.timezone import localtime
from django.conf import settings
import hashlib
import urllib

register = template.Library()


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
