
import django
from web.models import *
from web.utils import get_hash_name
import logging
import feedparser

logger = logging.getLogger(__name__)


def parse_atom(feed_url):
    """
    解析普通的 RSS 源
    :param feed_url:
    :return: 解析结果，成功字典；失败 None
    """
    feed_obj = feedparser.parse(feed_url)

    if feed_obj.feed.get('title'):
        name = get_hash_name(feed_url)
        cname = feed_obj.feed.title[:20]

        if feed_obj.feed.get('link'):
            link = feed_obj.feed.link[:1024]
        else:
            link = feed_url

        if feed_obj.feed.get('subtitle'):
            brief = feed_obj.feed.subtitle[:100]
        else:
            brief = cname

        author = feed_obj.feed.get('author', '')[:12]
        favicon = f"https://cdn.v2ex.com/gravatar/{name}?d=monsterid&s=64"

        try:
            site = Site(name=name, cname=cname, link=link, brief=brief, star=9, freq='小时', copyright=30, tag='RSS',
                        creator='user', rss=feed_url, favicon=favicon, author=author)
            site.save()
        except django.db.utils.IntegrityError:
            logger.info(f"源已经存在：`{feed_url}")
        except:
            logger.error(f'处理源出现未知异常：`{feed_url}')

        return {"name": name}
    else:
        logger.warning(f"RSS解析失败：`{feed_url}")

    return None
