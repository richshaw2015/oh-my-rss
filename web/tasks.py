
from web.models import *
import logging
from datetime import datetime
import datetime as dt
from django.utils.timezone import timedelta
from web.rssparser.atom import atom_spider
from web.rssparser.mpwx import make_mpwx_job, parse_list_page, parse_detail_page
from web.utils import is_active_rss, set_similar_article, get_similar_article, cal_cosine_distance, \
    get_user_subscribe_feeds, set_feed_ranking_dict, write_dat_file, is_updated_site, get_host_name, \
    reset_recent_articles, reset_recent_site_articles, set_site_lastid, set_active_sites, get_recent_articles, \
    get_user_visit_days, set_user_ranking_list, reset_sites_lastids, split_cn_words, get_active_sites, set_indexed, \
    is_indexed, set_job_stat, set_job_dvcs
from web.stopwords import stopwords
from bs4 import BeautifulSoup
from collections import Counter
from django.conf import settings
import jieba
import json
import os
from web.sql import JOB_STAT_SQL
import time


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
    job = Job.objects.get(pk=job_id, status=1)

    if job.url == job_url:
        job.rsp = rsp
        job.rsp_url = rsp_url

        if job.action in (10, 11, 12, 13):
            status = parse_list_page(job)
        elif job.action in (20, 21, 22, 23):
            status = parse_detail_page(job)
        else:
            logger.warning(f"未知的任务类型：`{job.action}")
            return False

        job.status = status
        if status == 2:
            job.rsp = ''
        job.save()
    else:
        logger.warning(f"任务不匹配：`{job.id}`{job.url}`{job_url}")
        return False

    return True


def update_all_atom_cron():
    """
    定时更新所有源，1～2 小时的周期
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


def update_all_mpwx_cron():
    """
    更新微信公众号，每天 1 次；公众号的全部都会更新，且评级最低 10
    """
    # 暂时只更新瓦斯阅读的，其他需要分布式环境搭建好
    sites = Site.objects.filter(status='active', creator='wemp', rss__contains='qnmlgb.tech').order_by('-star')

    for site in sites:
        host, action = get_host_name(site.rss), None

        if 'ershicimi.com' in host:
            action = 11
        elif 'qnmlgb.tech' in host:
            action = 10
        elif 'wemp.app' in host:
            action = 12
        elif 'chuansongme.com' in host:
            action = 13
        else:
            logger.warning(f"未知的公众号域名：`{host}`{site.cname}")

        if action is not None:
            make_mpwx_job(site, action)

    return True


def archive_article_cron():
    """
    归档并清理文章，每天一次
    """
    # (, 10)，直接删除
    Article.objects.filter(site__star__lt=10, is_recent=False).delete()

    # [10, )，转移存储到磁盘
    articles = Article.objects.filter(site__star__gte=10, is_recent=False).order_by('-id').iterator()

    for article in articles:
        if not article.content.strip():
            break

        if write_dat_file(article.uindex, article.content):
            article.content = ' '
            article.save()

    # 清理数据
    lastmonth = datetime.now() - timedelta(days=30)
    Job.objects.filter(ctime__lt=lastmonth).delete()

    return True


def cal_all_article_tag_cron():
    """
    设置最近一周的文章标识、统计词频；每隔 ？ 分钟
    """
    # 设置最近一周文章标识
    lastweek = datetime.now() - timedelta(days=7)

    Article.objects.filter(is_recent=True, ctime__lte=lastweek).update(is_recent=False)

    # 扫描空 tag 然后统计词频
    articles = Article.objects.filter(is_recent=True, status='active', site__star__gte=10, tags='').order_by('-id')

    for article in articles:
        content_soup = BeautifulSoup(article.content, 'html.parser')
        content_text = content_soup.get_text() + 3 * article.title
        seg_list = jieba.cut(content_text)
        words_list = []

        for seg in seg_list:
            seg = seg.strip().lower()

            if len(seg) > 1 and seg not in stopwords:
                words_list.append(seg)

        tags_list = dict(Counter(words_list).most_common(10))

        # 过滤只出现一次的
        tags_list = {k: v for k, v in tags_list.items() if v >= 2}

        if tags_list:
            logger.info(f'{article.uindex}`{tags_list}')

            article.tags = json.dumps(tags_list)
            article.save()

    return True


def cal_article_distance_cron():
    """
    计算新增文章的相似度，用于推荐订阅；每隔 ？ 分钟计算一次
    """
    articles = Article.objects.filter(is_recent=True, status='active', site__star__gte=10).exclude(tags='').\
        order_by('-id')

    lastmonth = datetime.now() - timedelta(days=30)

    for article in articles:
        similar_dict = {}

        if not get_similar_article(article.uindex):
            # 和过去一个月的文章对比
            compare_articles = Article.objects.filter(status='active', site__star__gte=10, ctime__gt=lastmonth).\
                exclude(tags='').values('uindex', 'tags')

            for compare in compare_articles:
                src_tags = json.loads(article.tags)
                dest_tags = json.loads(compare['tags'])
                distance = cal_cosine_distance(src_tags, dest_tags)

                if 0.1 < distance < 1:
                    similar_dict[compare['uindex']] = distance

            if similar_dict:
                sorted_similar_dict = dict(sorted(similar_dict.items(), key=lambda v: v[1], reverse=True)[:10])

                logger.info(f'{article.uindex}`{sorted_similar_dict}')

                set_similar_article(article.uindex, sorted_similar_dict)

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
    建立全文搜索索引
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

        if article.content.strip():
            title = split_cn_words(article.title, join=True)
            author = article.author or ''

            content_soup = BeautifulSoup(article.content, 'html.parser')
            content = split_cn_words(content_soup.get_text(), join=True)

            logger.info(f"分词结果：`{uindex}`{title}")

            try:
                idx_writer.add_document(uindex=uindex, title=title, author=author, content=content)
                set_indexed('article', uindex)
            except:
                logger.warning(f"索引失败：`{uindex}")
    idx_writer.commit()

    # 清理过期文章
    lastweek_ts = int(time.time() * 1000) - 7*86400*1000
    query = QueryParser("uindex", idx.schema).parse('uindex:{to %s]' % lastweek_ts)

    with idx.searcher() as searcher:
        idx_writer.delete_by_query(query, searcher)
        idx_writer.commit()

    return True


def clear_expired_job_cron():
    onehour = datetime.now() - timedelta(hours=1)

    # 过期任务状态变更，最多执行 1 小时
    affected = Job.objects.filter(status=1, mtime__lt=onehour).update(status=3)

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
