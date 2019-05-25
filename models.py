from django.db import models
import django.utils.timezone as timezone


class Page(models.Model):

    class Meta:
        unique_together = ('title', 'author_name')

    title = models.CharField('标题', max_length=100)
    author_name = models.CharField('作者', max_length=200)
    author_url = models.CharField('作者主页', max_length=200)
    link = models.CharField('地址', max_length=1000)
    content = models.TextField('html内容')
    summary = models.TextField('概览', default='')
    category = models.CharField('分类', max_length=1000, default='')

    is_delete = models.BooleanField('是否删除', default=False)
    is_recommend = models.BooleanField('是否推荐', default=False)

    updated = models.DateTimeField('修改时间', default=timezone.now)
    published = models.DateTimeField('创建时间', default=timezone.now)

    remark = models.CharField('备注', max_length=1000, null=True)
