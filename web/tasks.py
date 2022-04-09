
from web.models import *
import logging
from datetime import datetime
from django.utils.timezone import timedelta
from web.rssparser.atom import atom_spider
from web.rssparser.podcast import podcast_spider
from web.utils import is_active_rss, get_user_subscribe_feeds, set_feed_ranking_dict, is_indexed, del_dat2_file, \
    reset_recent_articles, reset_recent_site_articles, set_site_lastid, set_active_sites, \
    get_user_visit_days, set_user_ranking_list, reset_sites_lastids, split_cn_words, get_active_sites, set_indexed
from collections import Counter
from django.conf import settings
from django.db.models import Count
import json
import os


logger = logging.getLogger(__name__)


def update_all_atom_cron():
    """
    定时更新所有普通源
    """
    # 按照不同频率更新，区分用户自定义的和推荐的
    sites = Site.objects.filter(status='active', creator='user').order_by('-star')

    for site in sites:
        # 无人订阅的源不更新
        if not is_active_rss(site.pk):
            continue

        atom_spider(site)

    load_articles_to_redis_cron()
    load_active_sites_cron()
    return True


def update_all_podcast_cron():
    """
    更新播客
    """
    sites = Site.objects.filter(status='active', creator='podcast').order_by('-star')
    for site in sites:
        podcast_spider(site)

    load_articles_to_redis_cron()
    load_active_sites_cron()
    return True


def archive_article_cron():
    """
    归档并清理文章
    """
    # 变更最近文章标示
    recent_ts = datetime.now() - timedelta(days=settings.RECENT_DAYS)
    Article.objects.filter(is_recent=True, ctime__lte=recent_ts).update(is_recent=False)

    for dest in Article.objects.values("site_id").annotate(count=Count('site_id')).\
            filter(count__gt=settings.MAX_ARTICLES):
        for article in Article.objects.filter(site_id=dest['site_id']).order_by('-id')[settings.MAX_ARTICLES:]:
            if not article.is_recent:
                del_dat2_file(article.uindex, article.site_id)
                article.delete()
    return True


def cal_user_ranking_cron():
    """
    计算用户活跃排行榜
    """
    visit_ranking_list, dest_ranking_list = [], []

    for user in User.objects.all().iterator():
        visit_ranking_list.append((user.pk, get_user_visit_days(user.oauth_id)))

    visit_ranking_list = sorted(visit_ranking_list, key=lambda v: v[1], reverse=True)[:30]

    for board in visit_ranking_list:
        user = User.objects.get(pk=board[0])
        ext = json.loads(user.oauth_ext)

        dest_ranking_list.append({
            "score": board[1],
            "name": user.oauth_name,
            "avatar": user.avatar,
            "level": user.level,
            "url": ext.get('html_url'),
            "intro": ext.get('bio') or ext.get('company') or ext.get('location')
        })

    return set_user_ranking_list(dest_ranking_list)


def cal_site_ranking_cron():
    """
    计算订阅排行榜单 top 100，每天 1 次
    """
    users = User.objects.all().values_list('oauth_id', flat=True)

    all_user_feeds = []
    dest_feed_ranking = []

    for oauth_id in users:
        all_user_feeds += get_user_subscribe_feeds(oauth_id, from_user=False, user_level=99)

    feed_ranking = dict(Counter(all_user_feeds).most_common(100))

    for (site_id, score) in feed_ranking.items():
        try:
            site_dict = Site.objects.get(pk=site_id, status='active').__dict__
            del site_dict['_state'], site_dict['ctime'], site_dict['mtime']
            site_dict['score'] = score
        except:
            logger.warning(f"订阅源不存在：`{site_id}")
            continue

        dest_feed_ranking.append(site_dict)

    set_feed_ranking_dict(dest_feed_ranking)

    return True


def load_articles_to_redis_cron():
    """
    扫描一遍数据库
    """
    site_articles, articles, sites_lastids = {}, [], []

    for article in Article.objects.filter(status='active', is_recent=True).order_by('-id').iterator():
        # 所有文章的索引
        articles.append(article.uindex)

        # 所有文章站点的索引
        if not site_articles.get(article.site_id):
            site_articles[article.site_id] = [article.uindex, ]
        else:
            site_articles[article.site_id].append(article.uindex)

    # 更新缓存
    reset_recent_articles(articles)

    for (site_id, update_list) in site_articles.items():
        sites_lastids.append(update_list[0])

        # 更新缓存
        reset_recent_site_articles(site_id, update_list)
        set_site_lastid(site_id, update_list[0])

    # 所有站点的最后一条更新记录
    reset_sites_lastids(sites_lastids[:100])

    return True


def load_active_sites_cron():
    sites = Site.objects.filter(status='active').values_list('pk', flat=True)
    set_active_sites(sites)
    return True


def build_whoosh_index_cron():
    """
    建立全文搜索索引
    """
    from web.utils import whoosh_site_schema
    from whoosh.filedb.filestore import FileStorage

    idx_dir = settings.WHOOSH_IDX_DIR
    first_boot = False

    if not os.path.exists(idx_dir):
        os.makedirs(idx_dir)
        first_boot = True

    storage = FileStorage(idx_dir)

    if first_boot:
        idx = storage.create_index(whoosh_site_schema, indexname="site")
    else:
        idx = storage.open_index(indexname="site", schema=whoosh_site_schema)

    idx_writer = idx.writer()

    for site_id in get_active_sites():
        # 判断是否已经索引
        if is_indexed('site', site_id) and not first_boot:
            continue

        try:
            site = Site.objects.get(pk=site_id, status='active')
        except:
            continue

        cname = split_cn_words(site.cname, join=True)
        author = site.author or ''
        brief = split_cn_words(site.brief, join=True)

        logger.info(f"源分词结果：`{site_id}`{cname}`{brief}")

        try:
            idx_writer.add_document(id=site_id, cname=cname, author=author, brief=brief)
            set_indexed('site', site_id)
        except:
            logger.warning(f"源索引失败：`{site_id}")
    idx_writer.commit()

    return True
