# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from feed.utils import *
from scrapy.exceptions import DropItem
import django
import urllib
from bs4 import BeautifulSoup
import lxml.etree as etree
import re

# to use django models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ohmyrss.settings")
django.setup()

from web.models import *


class ValidPipeline(object):

    def process_item(self, item, spider):

        if item['title'] and item['content'] and item['url'] and item['name'] and item['req_url']:
            if 'github' in item['url'] and '，禁止转载' in item['content']:
                return DropItem(f"Data not allowed`{item}")
            else:
                return item
        else:
            raise DropItem(f"Data not valid`{item}")


class DomPipeline(object):
    """
    handle dom structure
    """

    def process_item(self, item, spider):
        content_soup = BeautifulSoup(item['content'], "html.parser")

        # to absolute external href
        for a in content_soup.find_all('a'):
            rel_href = a.attrs.get('href')
            abs_href = urllib.parse.urljoin(item['url'], rel_href)
            a.attrs['href'] = abs_href
            a.attrs['target'] = '_blank'

        # to absolute src
        for img in content_soup.find_all('img'):
            if img.attrs.get('file'):
                img.attrs['src'] = img.attrs['file']
            elif img.attrs.get('data-src'):
                img.attrs['src'] = img.attrs['data-src']
            try:
                for attr in ('srcset', 'data-srcset', 'data-s', 'data-w', 'data-type', 'data-ratio'):
                    del img.attrs[attr]
            except KeyError:
                pass

            rel_src = img.attrs.get('src')
            abs_src = urllib.parse.urljoin(item['url'], rel_src)
            img.attrs['src'] = abs_src
        # code style
        for pre in content_soup.find_all('pre'):
            try:
                del pre.attrs['style']
            except KeyError:
                pass

        # deny exec js
        for script in content_soup.find_all('script'):
            script.name = 'noscript'

        # for tencent crayon code theme, keep space symbols
        for s in content_soup.find_all('span', class_='crayon-h'):
            s.attrs['style'] = "white-space:pre;"

        # reset span font size
        for span in (content_soup.find_all('span') + content_soup.find_all('p')):
            if span.attrs.get('style'):
                span.attrs['style'] = re.sub(r'font-size\s*:\s*[^;]+;', '', span.attrs['style'])

        # trim style tags
        if item.get('trim_style_tags'):
            for tag in item['trim_style_tags']:
                for t in content_soup.find_all(tag):
                    if t.attrs.get('style'):
                        t.attrs['style'] = ''

        # trim contents
        if item.get('trims'):
            content_etree = etree.fromstring(str(content_soup), etree.HTMLParser())
            for xpath in item['trims']:
                for node in content_etree.xpath(xpath):
                    node.getparent().remove(node)
            item['content'] = etree.tostring(content_etree, pretty_print=False, encoding="utf-8").decode('utf8')
        else:
            item['content'] = str(content_soup)

        # add custom css
        if item.get('css'):
            item['content'] = f"""<style>%s</style>%s""" % (item.get('css'), item['content'])
        return item


class InsertDBPipeline(object):

    def process_item(self, item, spider):
        site = Site.objects.get(name=item['name'])

        if site.status == 'active':
            try:
                article = Article(site=site, title=item['title'], uindex=current_ts(), content=item['content'],
                                  remark='', src_url=item['url'])
                article.save()

                # mark status
                mark_crawled_url(item['url'], item['req_url'])
            except django.db.utils.IntegrityError:
                # repeat item
                mark_crawled_url(item['url'], item['req_url'])
