
from django import template

register = template.Library()


@register.filter
def to_stars(num):
    return '★' * num
