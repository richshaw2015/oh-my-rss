
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from web.models import *
from web.utils import add_referer_stats, get_login_user, get_user_subscribe_feeds, set_user_read_article, \
    split_cn_words
import logging
from user_agents import parse
from web.verify import verify_request
from django.conf import settings
from web.utils import whoosh_site_schema
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import MultifieldParser


logger = logging.getLogger(__name__)


def article(request, pid):
    """
    详情页，主要向移动端、搜索引擎提供，这个页面需要做风控
    """
    # 外链统计
    add_referer_stats(request.META.get('HTTP_REFERER', ''))

    try:
        article = Article.objects.get(uindex=pid, status='active')
    except:
        return HttpResponseRedirect('https://dinorss.org/')

    user = get_login_user(request)
    if user:
        set_user_read_article(user.oauth_id, pid)

    # 判断是否命中敏感词
    # if is_sensitive_content(pid, article.site_id):
    #     user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    #
    #     if user_agent.is_mobile or user_agent.is_bot:
    #         logger.warning(f'文章命中了敏感词，转到原文：`{article.title}`{pid}')
    #         return redirect(article.src_url)
    #     else:
    #         logger.warning(f'文章命中了敏感词，禁止访问：`{article.title}`{pid}')
    #         return redirect('index')

    context = dict()
    context['article'] = article
    context['user'] = user

    return render(request, 'mobile/article.html', context=context)


def robots(request):
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

    if user_agent.is_bot:
        return HttpResponse(f'''User-agent: *\nDisallow: /dashboard\n\nSitemap: /sitemap.txt''')

    return HttpResponseNotFound("Param Error")


def sitemap(request):
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    if user_agent.is_bot:
        indexs = Article.objects.filter(status='active', site__star__gte=10).order_by('-id').\
            values_list('uindex', flat=True)[:1000]

        url = request.build_absolute_uri('/')[:-1].strip("/").replace('http://', 'https://')
        sites = [f'{url}/post/{index}' for index in indexs]

        return HttpResponse('\n'.join(sites))

    return HttpResponseNotFound("Param Error")


@verify_request
def in_site_search(request):
    """
    站内搜索
    """
    user = get_login_user(request)
    keyword = request.POST.get('keyword', '').strip()
    scope = request.POST.get('scope', 'all')

    logger.warning(f"搜索关键字：`{keyword}")
    keyword = split_cn_words(keyword, join=True)
    logger.info(f"转换后的关键字：`{keyword}")

    if scope != 'all':
        return HttpResponseForbidden('Param Error')

    if not keyword:
        return HttpResponseNotFound("Empty Keyword")

    storage = FileStorage(settings.WHOOSH_IDX_DIR)

    # 查找相关源
    idx = storage.open_index(indexname="site", schema=whoosh_site_schema)
    qp = MultifieldParser(['cname', 'author', 'brief'], schema=whoosh_site_schema)
    query = qp.parse(keyword)
    sites = []

    with idx.searcher() as s:
        results = s.search(query, limit=50)

        for ret in results:
            sites.append(ret['id'])

    rel_sites = Site.objects.filter(status='active', pk__in=sites).order_by('-star')

    # 用户订阅
    user_sub_feeds = []
    if user:
        user_sub_feeds = get_user_subscribe_feeds(user.oauth_id, user_level=user.level)

    context = dict()
    context['user'] = user
    context['user_sub_feeds'] = user_sub_feeds
    context['rel_sites'] = rel_sites
    context['keyword'] = keyword

    return render(request, 'search/search.html', context=context)
