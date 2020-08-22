from django.http import JsonResponse
from web.utils import *
from feed.utils import mkdir
import logging
from web.models import *
import shutil

logger = logging.getLogger(__name__)

wemp_dict = {}


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
    articles = Article.objects.filter(status='active').iterator()
    for article in articles:
        mkdir(os.path.join(settings.HTML_DATA2_DIR, str(article.site_id)))
        new_file = os.path.join(settings.HTML_DATA2_DIR, str(article.site_id), f"{article.uindex}.html")
        old_file = os.path.join(settings.HTML_DATA_DIR, str(article.uindex))

        # 不存在时才新建
        if not os.path.exists(new_file):
            if os.path.exists(old_file):
                shutil.copyfile(old_file, new_file)
            elif article.content.strip():
                write_dat2_file(article.uindex, article.site_id, article.content)
            else:
                logger.warning(f"文件同步失败：`{article.uindex}")
    # 收藏文章
    articles = UserArticle.objects.all().iterator()
    for article in articles:
        mkdir(os.path.join(settings.HTML_DATA2_DIR, str(article.site_id)))
        new_file = os.path.join(settings.HTML_DATA2_DIR, str(article.site_id), f"{article.uindex}.html")
        old_file = os.path.join(settings.HTML_DATA_DIR, str(article.uindex))

        # 不存在时才新建
        if not os.path.exists(new_file):
            if os.path.exists(old_file):
                shutil.copyfile(old_file, new_file)
            else:
                logger.warning(f"旧文件查找失败：`{article.uindex}")
    return JsonResponse({})


def debug(request):
    # from web.rssparser.mpwx import make_mpwx_job
    # site = Site.objects.get(pk=2910)
    # make_mpwx_job(site, 14)

    from web.tasks import build_whoosh_index_cron
    build_whoosh_index_cron()

    return JsonResponse({})
