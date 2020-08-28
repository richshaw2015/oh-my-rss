from django.http import JsonResponse
from web.utils import *
from feed.utils import mkdir
import logging
from web.models import *
import shutil
import feedparser

logger = logging.getLogger(__name__)


def load_db_data(request):
    """
    加载文章数据到内存，调试使用
    """
    user = get_login_user(request)

    if user or settings.DEBUG:
        from web.tasks import load_articles_to_redis_cron, load_active_sites_cron

        load_active_sites_cron()
        load_articles_to_redis_cron()

        return JsonResponse({})


def install(request):
    """
    部署后操作
    """
    return JsonResponse({})


def debug(request):
    from web.rssparser.podcast import podcast_spider
    from web.rssparser.atom import atom_spider

    # site = Site.objects.get(pk=3345)
    # podcast_spider(site)
    sites = Site.objects.filter(status='active', creator='user')
    for site in sites:
        feed_obj = feedparser.parse(site.rss)

        if is_podcast_feed(feed_obj):
            logger.info(f"发现目标：`{site.id}`{site.cname}`{site.rss}")

            if feed_obj.feed.get('image'):
                favicon = save_avatar(feed_obj.feed.image.href, site.name)
                site.favicon = favicon

            if site.star < 10:
                site.star = 10

            if feed_obj.feed.get('subtitle'):
                brief = get_html_text(feed_obj.feed.subtitle)[:200]
                site.brief = brief

            site.creator = 'podcast'
            site.save()

    return JsonResponse({})
