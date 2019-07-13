from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import *
import time


def get_article_detail(request):
    """
    获取文章详情
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')
    uindex = request.POST.get('id')
    article = Article.objects.get(uindex=uindex)
    context = dict()
    context['article'] = article
    time.sleep(0.5)
    return render(request, 'article.html', context=context)


def get_issues_html(request):
    """
    获取留言页面
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uuid = request.POST.get('uid')
    # TODO 适配内容
    context = dict()
    return render(request, 'issues.html', context=context)


def get_feeds_html(request):
    """
    获取订阅列表
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uuid = request.POST.get('uid')
    feeds = Site.objects.filter(status='active')
    context = dict()
    context['feeds'] = feeds
    return render(request, 'feeds.html', context=context)


def get_settings_html(request):
    """
    获取设置页面
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uuid = request.POST.get('uid')
    time.sleep(1)
    return render(request, 'settings.html')
