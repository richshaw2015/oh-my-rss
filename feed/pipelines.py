# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from feed.utils import *
from scrapy.exceptions import DropItem
import django
from bs4 import BeautifulSoup

# 使用django的模型，需要初始化环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ohmyrss.settings")
django.setup()

from web.models import *


class ValidPipeline(object):
    """
    合法性判断
    """
    def process_item(self, item, spider):

        if item['title'] and item['content'] and item['url'] and item['name']:
            return item
        else:
            raise DropItem("数据校验失败：%s" % item)


class DomPipeline(object):
    """
    页面结构处理
    """
    def process_item(self, item, spider):
        content_soup = BeautifulSoup(item['content'], "html.parser")

        # 图片点击处理
        # for img in content_soup.find_all('img'):
        #    if img.attrs.get('class'):
        #        img.attrs['class'] += ' materialboxed'
        #    else:
        #        img.attrs['class'] = 'materialboxed'

        # 外链处理
        for a in content_soup.find_all('a'):
            rel_href = a.attrs.get('href')
            abs_href = urllib.parse.urljoin(item['url'], rel_href)
            a.attrs['href'] = abs_href
            a.attrs['target'] = '_blank'

        # 屏蔽 js 执行
        for script in content_soup.find_all('script'):
            script.name = 'noscript'

        item['content'] = content_soup.prettify()
        return item


class TodbPipeline(object):
    """
    插入数据库
    """
    def process_item(self, item, spider):
        site_obj = Site.objects.get(name=item['name'])

        if site_obj.status == 'active':
            article_obj = Article(site=site_obj, title=item['title'], uindex=current_ts(), content=item['content'],
                                  remark='', src_url=item['url'])
            article_obj.save()

            # 更新标记
            set_crawled_url(item['url'])
        else:
            # TODO 站点被下线处理
            pass
