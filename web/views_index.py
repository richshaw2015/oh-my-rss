from django.shortcuts import render
from .models import *
from .utils import get_client_ip
import logging

logger = logging.getLogger(__name__)


def index(request):
    """
    index home page
    :param request:
    :return:
    """
    logger.info("收到首页请求：`%s", get_client_ip(request))

    # render default article list
    articles = Article.objects.filter(status='active').order_by('-id')[:10]

    context = dict()
    context['articles'] = articles

    return render(request, 'index.html', context)


