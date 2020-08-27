
import django
from web.models import *
from web.utils import generate_rss_avatar, set_updated_site, get_with_retry, get_short_host_name, write_dat2_file, \
    save_avatar, get_html_text, to_podcast_duration
import logging
import feedparser
import json
from io import BytesIO
from feed.utils import current_ts, mark_crawled_url, is_crawled_url, get_hash_name

logger = logging.getLogger(__name__)

podcast_tmpl = '''<div id='omrss-podlove' data-episode='%s'>
  <root style="max-width:950px;min-width:260px;">
    <div class="tablet:px-6 tablet:pt-6 mobile:px-4 mobile:pt-4 flex flex-col">
      <div class="flex-col items-center mobile:flex tablet:hidden">
        <show-title class="text-sm"></show-title>
        <episode-title class="text-base mb-2"></episode-title>
        <subscribe-button
          class="mb-4 mobile:flex tablet:hidden"
        ></subscribe-button>
        <poster class="rounded-sm w-48 shadow overflow-hidden"></poster>
        <divider class="w-full my-6"></divider>
      </div>

      <div class="tablet:flex flex-grow">
        <div class="w-64 mobile:hidden tablet:block tablet:mr-6">
          <poster class="rounded-sm shadow overflow-hidden"></poster>
        </div>
        <div class="w-full">
          <div class="hidden tablet:block">
            <show-title class="text-base"></show-title>
            <episode-title class="text-xl desktop:text-2xl"></episode-title>
            <divider class="w-full my-4"></divider>
          </div>
          <div class="flex items-center justify-between">
            <div class="block">
              <play-state on="active">
                <speed-control
                  class="block hidden tablet:block"
                ></speed-control>
              </play-state>
            </div>

            <div class="flex">
              <play-state on="active">
                <chapter-previous class="mx-2 block"></chapter-previous>
              </play-state>
              <play-state on="active">
                <step-backward class="mx-2 block"></step-backward>
              </play-state>

              <play-button class="mx-2 block" label="播放"></play-button>

              <play-state on="active">
                <step-forward class="mx-2 block"></step-forward>
              </play-state>
              <play-state on="active">
                <chapter-next class="mx-2 block"></chapter-next>
              </play-state>
            </div>

            <div class="block">
              <play-state on="active">
                <volume-control
                  class="flex items-center hidden tablet:flex"
                ></volume-control>
              </play-state>
            </div>
          </div>
          <div class="flex w-full">
            <progress-bar></progress-bar>
          </div>
          <div class="flex w-full -mt-2">
            <div class="w-3/12 text-left">
              <timer-current class="text-sm"></timer-current>
            </div>
            <div class="w-6/12 text-center">
              <play-state on="active">
                <current-chapter class="text-sm truncate"></current-chapter>
              </play-state>
            </div>
            <div class="w-3/12 text-right">
              <timer-duration class="text-sm"></timer-duration>
            </div>
          </div>
        </div>
      </div>
      <div class="w-full mt-6 mb-3"></div>
    </div>
    <error></error>
  </root>
</div>'''


def add_postcast_feed(feed_obj):
    """
    播客类型的 RSS 源
    :param feed_obj:
    :return: 解析结果，成功字典；失败 None
    """
    url = feed_obj.url

    if feed_obj.feed.get('title'):
        name = get_hash_name(url)

        site = Site.objects.filter(name=name, status='active')
        if site:
            logger.info(f"源已经存在：`{url}")

            return {"site": site[0].pk}

        cname = feed_obj.feed.title[:50]

        try:
            link = feed_obj.feed.content_detail.base
        except AttributeError:
            if feed_obj.feed.get('link'):
                link = feed_obj.feed.link[:1024]
            else:
                link = url

        if feed_obj.feed.get('subtitle'):
            brief = get_html_text(feed_obj.feed.subtitle)[:200]
        else:
            brief = feed_obj.feed.title

        try:
            author = feed_obj.feed.author_detail.name
        except AttributeError:
            author = feed_obj.feed.get('author') or get_short_host_name(link)

        # 使用默认头像
        if feed_obj.feed.get('image'):
            favicon = save_avatar(feed_obj.feed.image.href, name)
        else:
            favicon = generate_rss_avatar(link)

        try:
            site = Site(name=name, cname=cname, link=link, brief=brief, star=10, copyright=30,
                        creator='podcast', rss=url, favicon=favicon, author=author)
            site.save()

            return {"site": site.pk}
        except:
            logger.error(f'新增播客异常：`{url}')
    else:
        logger.warning(f"播客解析失败：`{url}")

    return None


def podcast_spider(site):
    """
    更新源内容
    """
    resp = get_with_retry(site.rss)

    if resp is None:
        logger.info(f"RSS 源可能失效了`{site.rss}")
        return None

    feed_obj = feedparser.parse(BytesIO(resp.content))

    for entry in feed_obj.entries[:12]:
        # 有些是空的
        if not entry:
            continue

        try:
            title = entry.title
            link = entry.link
        except AttributeError:
            logger.warning(f'必要属性获取失败：`{site.rss}')
            continue

        if is_crawled_url(link):
            continue

        try:
            author = entry['author'][:20]
        except:
            author = ''

        audio, img = None, ''
        if entry.get('links'):
            for el in entry['links']:
                if 'audio/' in el.type:
                    audio = el
                    break

        if entry.get('image'):
            img = entry.image.href

        try:
            brief = entry.content[0].value
        except:
            brief = entry.get('description') or entry.link

        if audio is not None:
            # 生成 podlove 所需数据
            episode = {
                "version": 5,
                "show": {
                    "title": site.cname,
                    "subtitle": site.brief,
                    "poster": site.favicon,
                    "link": site.link,
                },
                "title": title,
                "link": link,
                # "subtitle": brief,
                "publicationDate": entry.get('published'),
                "poster": img,
                "duration": to_podcast_duration(entry.get('itunes_duration')),
                "audio": [
                    {
                        "url": audio.href,
                        "mimeType": audio.type
                    }
                ]
            }
            episode = json.dumps(episode)
            content = podcast_tmpl % episode + brief
        else:
            content = brief + f'''<p></p><img src="{img}">'''

        try:
            uindex = current_ts()

            article = Article(site=site, title=title, author=author, src_url=link, uindex=uindex)
            article.save()

            write_dat2_file(uindex, site.id, content)

            mark_crawled_url(link)
        except django.db.utils.IntegrityError:
            logger.info(f'数据重复插入：`{title}`{link}')
            mark_crawled_url(link)
        except:
            logger.warning(f'数据插入异常：`{title}`{link}')

    set_updated_site(site.pk)
    return True
