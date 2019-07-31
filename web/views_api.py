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
    return render(request, 'article/index.html', context=context)


def get_feeds_html(request):
    """
    获取订阅列表
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')
    feeds = Site.objects.filter(status='active').order_by('-star')
    context = dict()
    context['feeds'] = feeds
    return render(request, 'ajax/myfeeds.html', context=context)


def get_homepage_html(request):
    """
    获取首页介绍
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')
    return render(request, 'ajax/intro.html')


def get_issues_html(request):
    """
    获取首页介绍
    :param request:
    :return:
    """
    # TODO 校验 uid 合法性
    uid = request.POST.get('uid')

    msgs = Message.objects.filter(status='active').order_by('-id')[:100]
    context = dict()
    context['msgs'] = msgs
    return render(request, 'ajax/issues.html', context=context)
