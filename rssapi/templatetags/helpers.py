
from django import template

register = template.Library()


@register.filter
def to_stars(num):
    """
    转换成星星评级（1，2，3）
    :param num:
    :return:
    """
    return '★' * int(num / 10)


@register.filter
def to_date_fmt(dt):
    """
    转换成 "YYYY-MM-DD hh:mm:ss" 格式的时间
    :param dt:
    :return:
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")

