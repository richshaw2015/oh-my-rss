
from web.models import *
import logging
from datetime import datetime
import datetime as dt
from django.utils.timezone import timedelta
from feed.utils import current_ts
from web.rssparser.atom import atom_spider
from web.rssparser.podcast import podcast_spider
from web.rssparser.mpwx import make_mpwx_job, parse_list_page, parse_detail_page
from web.utils import is_active_rss, get_user_subscribe_feeds, set_feed_ranking_dict, get_content, \
    is_updated_site, get_host_name, is_indexed, set_job_stat, set_job_dvcs, del_dat2_file, \
    reset_recent_articles, reset_recent_site_articles, set_site_lastid, set_active_sites, get_recent_articles, \
    get_user_visit_days, set_user_ranking_list, reset_sites_lastids, split_cn_words, get_active_sites, set_indexed
from bs4 import BeautifulSoup
from collections import Counter
from django.conf import settings
import json
import os
from web.sql import JOB_STAT_SQL


logger = logging.getLogger(__name__)


def update_sites_async(sites, force_update=False):
    """
    异步更新某一批订阅源，只支持普通源
    """
    for site_id in sites:
        try:
            site = Site.objects.get(status='active', pk=site_id, creator='user')
        except:
            continue

        # 最近已经更新过了，跳过
        if not force_update and is_updated_site(site_id):
            continue

        logger.info(f"开始异步更新：{site_id}")
        atom_spider(site)

    return True


def handle_job_async(job_id, job_url, rsp, rsp_url):
    """
    处理入库任务
    """
    try:
        job = Job.objects.get(pk=job_id, status__in=(1, 3, 8))
    except:
        return False

    if job.url == job_url:
        job.rsp = rsp
        job.rsp_url = rsp_url

        if job.action in (10, 11, 12, 13, 14):
            status = parse_list_page(job)
        elif job.action in (20, 21, 22, 23, 24):
            status = parse_detail_page(job)
        else:
            logger.warning(f"未知的任务类型：`{job.action}")
            return False

        job.status = status
        if status == 2:
            job.rsp = ''
        job.save()
        return True
    else:
        logger.warning(f"任务不匹配：`{job.id}`{job.url}`{job_url}")

    return False


def update_all_atom_cron():
    """
    定时更新所有普通源
    """
    now, sites = datetime.now(), []

    # 按照不同频率更新，区分用户自定义的和推荐的
    if now.hour % 2 == 0:
        sites = Site.objects.filter(status='active', creator='user').order_by('-star')
    elif now.hour % 2 == 1:
        sites = Site.objects.filter(status='active', creator='user', star__gte=9).order_by('-star')

    for site in sites:
        # 无人订阅的源且不推荐的源不更新
        if not is_active_rss(site.pk) and site.star < 9:
            continue

        # 是否已经更新过
        if not is_updated_site(site.pk):
            atom_spider(site)

    return True


def update_all_podcast_cron():
    """
    更新播客
    """
    sites = Site.objects.filter(status='active', creator='podcast').order_by('-star')
    for site in sites:
        podcast_spider(site)

    return True


def update_all_mpwx_cron():
    """
    更新微信公众号
    """
    sites = Site.objects.filter(status='active', creator='wemp').order_by('-star')

    for site in sites:
        host, action = get_host_name(site.rss), None

        if settings.QNMLGB_HOST in host or settings.ANYV_HOST in host or settings.ERSHICIMI_HOST in host:
            if settings.ERSHICIMI_HOST in host:
                action = 11
            elif settings.QNMLGB_HOST in host:
                action = 10
            elif settings.WEMP_HOST in host:
                action = 12
            elif settings.CHUANSONGME_HOST in host:
                action = 13
            elif settings.ANYV_HOST in host:
                action = 14
            else:
                logger.warning(f"未知的公众号域名：`{host}`{site.cname}")

            if action is not None:
                make_mpwx_job(site, action)

    return True


def archive_article_cron():
    """
    归档并清理文章
    """
    # (, 10)，没有收藏过把文件也删除了
    articles = Article.objects.filter(site__star__lt=10, is_recent=False).iterator()
    for article in articles:
        if not UserArticle.objects.filter(uindex=article.uindex).exists():
            del_dat2_file(article.uindex, article.site_id)

        article.delete()

    # TODO 每个源保留最近 1000 条文章

    # 清理 Job 数据
    deat_ts = datetime.now() - timedelta(days=7)
    Job.objects.filter(ctime__lt=deat_ts).delete()

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
    扫描一遍数据库，每隔 5 分钟同步一次
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
    建立全文搜索索引 TODO 优化索引效率
    """
    from web.utils import whoosh_site_schema, whoosh_article_schema
    from whoosh.filedb.filestore import FileStorage
    from whoosh.qparser import QueryParser

    idx_dir = settings.WHOOSH_IDX_DIR
    first_boot = False

    if not os.path.exists(idx_dir):
        os.makedirs(idx_dir)
        first_boot = True

    storage = FileStorage(idx_dir)

    # 索引站点
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

        logger.info(f"分词结果：`{site_id}`{cname}`{brief}")

        try:
            idx_writer.add_document(id=site_id, cname=cname, author=author, brief=brief)
            set_indexed('site', site_id)
        except:
            logger.warning(f"索引失败：`{site_id}")
    idx_writer.commit()

    # 索引文章
    if first_boot:
        idx = storage.create_index(whoosh_article_schema, indexname="article")
    else:
        idx = storage.open_index(indexname="article", schema=whoosh_article_schema)

    idx_writer = idx.writer()

    for uindex in get_recent_articles():
        # 判断是否已经索引
        if is_indexed('article', uindex) and not first_boot:
            continue

        try:
            article = Article.objects.get(uindex=uindex, status='active')
        except:
            continue

        content = get_content(uindex, article.site_id)

        if content:
            title = split_cn_words(article.title, join=True)
            author = article.author or ''

            content_soup = BeautifulSoup(content, 'html.parser')
            content = split_cn_words(content_soup.get_text(), join=True)

            logger.info(f"分词结果：`{uindex}`{title}")

            try:
                idx_writer.add_document(uindex=uindex, title=title, author=author, content=content)
                set_indexed('article', uindex)
            except:
                logger.warning(f"索引失败：`{uindex}")
    idx_writer.commit()

    # 清理过期文章
    idx = storage.open_index(indexname="article", schema=whoosh_article_schema)
    idx_writer = idx.writer()

    lastweek_ts = str(current_ts() - 7*86400*1000)
    query = QueryParser("uindex", idx.schema).parse('uindex:{to %s]' % lastweek_ts)

    with idx.searcher() as searcher:
        idx_writer.delete_by_query(query, searcher)
        idx_writer.commit()

    return True


def clear_expired_job_cron():
    timeout_ts = datetime.now() - timedelta(hours=6)

    # 过期任务状态变更，最多执行 1 小时
    affected = Job.objects.filter(status=1, mtime__lt=timeout_ts).update(status=3)

    if affected > 0:
        logger.warning(f"超时任务数量：`{affected}")

    return True


def cal_dvc_stat_cron():
    # 计算设备详情
    today_dt = datetime.now() - (datetime.now() - datetime.combine(dt.date.today(), dt.time()))
    job_stats = Job.objects.raw(JOB_STAT_SQL % today_dt)

    for stat in job_stats:
        set_job_stat(stat)

    # 计算总设备数
    dvcs = Job.objects.distinct().values_list('dvc_id', flat=True)
    set_job_dvcs(dvcs)

    return True
