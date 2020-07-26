from django.shortcuts import render
from web.models import *
from web.utils import add_referer_stats, get_login_user, get_user_subscribe_feeds, get_visitor_subscribe_feeds
import logging
from user_agents import parse
from django.conf import settings

logger = logging.getLogger(__name__)


def index(request):
    """
    index home page
    :param request:
    :return:
    """
    # PC 版、手机版适配
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    pc = user_agent.is_pc

    # 判断是否登录用户
    user = get_login_user(request)

    # 默认的渲染列表，区分是否登录用户
    if user is None:
        sub_feeds = get_visitor_subscribe_feeds('', '')
    else:
        sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

    pre_load_count = 1 if pc else 10

    articles = Article.objects.filter(status='active', site_id__in=sub_feeds).order_by('-id')[:pre_load_count]

    context = dict()
    context['articles'] = articles
    context['user'] = user
    context['github_oauth_key'] = settings.GITHUB_OAUTH_KEY

    # 记录访问来源
    add_referer_stats(request.META.get('HTTP_REFERER', ''))

    if pc:
        return render(request, 'index.html', context)
    else:
        return render(request, 'mobile/index.html', context)
