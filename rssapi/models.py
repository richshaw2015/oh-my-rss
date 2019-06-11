from django.db import models


class Site(models.Model):
    """
    内容站点定义
    """
    name = models.CharField('对应 scrapy 的 name 代号（不对外显示）', max_length=100, unique=True, db_index=True)
    cname = models.CharField('显示来源的名称', max_length=100)
    link = models.CharField('来源站点的主页', max_length=200)
    favico = models.CharField('图标地址，单独制作', max_length=100, default='')
    brief = models.CharField('来源站点的简介', max_length=200)
    star = models.IntegerField('评级', choices=(
        (1, '入门'),
        (2, '普通'),
        (3, '优秀'),
    ), default=2)
    freq = models.CharField('更新频率', choices=(
        ('日更', '每天更新'),
        ('周更', '每周更新'),
        ('月更', '每月更新'),
    ), max_length=20)
    status = models.CharField('状态，默认 active 激活，close 关闭', max_length=20, choices=(
        ('active', '激活'),
        ('close', '关闭，下线'),
    ), default='active')

    ctime = models.DateTimeField('创建时间', auto_now_add=True)
    mtime = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注', default='')


class Article(models.Model):
    """
    文章表
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    title = models.CharField('标题', max_length=200, unique=True)
    uindex = models.IntegerField('一个时间戳表示的唯一地址', unique=True, db_index=True)
    content = models.TextField('内容')
    status = models.CharField('状态', max_length=20, choices=(
        ('active', '激活'),
        ('close', '关闭，下线'),
    ), default='active')
    readtime = models.IntegerField('预计阅读时间，分钟', default=1)

    ctime = models.DateTimeField('创建时间', auto_now_add=True)
    mtime = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注', default='')
