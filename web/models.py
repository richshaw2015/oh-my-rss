from django.db import models


class Site(models.Model):
    """
    站点表
    """
    name = models.CharField('scrapy代号', max_length=100, unique=True)
    author = models.CharField('作者', max_length=100, null=True, blank=True, default='')
    cname = models.CharField('名称', max_length=100)
    link = models.CharField('主页', max_length=1024)
    favicon = models.CharField('favicon', max_length=100, default='', null=True, blank=True)
    brief = models.CharField('简介', max_length=200)
    star = models.IntegerField('评级', default=20, db_index=True)

    status = models.CharField('状态', max_length=20, choices=(
        ('active', '激活'),
        ('close', '关闭，下线'),
    ), default='active', db_index=True)
    copyright = models.IntegerField('版权', choices=(
        (0, '未知'),
        (10, '不可转载'),
        (20, '仅可转载摘要'),
        (30, '可以全文转载'),
    ), default=0, null=True, blank=True)

    rss = models.CharField('RSS地址', max_length=1024, null=True, blank=True)
    creator = models.CharField('创建人', choices=(
        ('system', '系统录入'),
        ('user', '用户提交'),
        ('wemp', '微信公众号'),
    ), max_length=20, null=True, blank=True, default='system', db_index=True)

    ctime = models.DateTimeField('创建时间', auto_now_add=True)
    mtime = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注', default='', null=True, blank=True)


class Article(models.Model):
    """
    文章表
    """

    class Meta:
        unique_together = [['src_url', 'site'],
                           ['title', 'site']]

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    title = models.CharField('标题', max_length=200)
    author = models.CharField('作者', max_length=100, null=True, blank=True)
    uindex = models.IntegerField('唯一地址', unique=True, db_index=True)
    content = models.TextField('内容')
    src_url = models.CharField('原始链接', max_length=1024)
    status = models.CharField('状态', max_length=20, choices=(
        ('active', '激活'),
        ('close', '关闭，下线'),
    ), default='active', db_index=True)

    is_recent = models.BooleanField('最近的文章', choices=(
        (True, '最近文章'),
        (False, '历史文章'),
    ), default=True, db_index=True)

    tags = models.TextField('词频', default='', null=True, blank=True)

    ctime = models.DateTimeField('创建时间', auto_now_add=True)
    mtime = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注', default='', null=True, blank=True)


class User(models.Model):
    """
    用户表，使用第三方的才会入库
    """
    oauth_id = models.CharField('平台+id', max_length=100, unique=True, db_index=True)
    oauth_name = models.CharField('昵称', max_length=100)
    oauth_avatar = models.CharField('头像', max_length=200)
    oauth_email = models.CharField('email', max_length=100, null=True, blank=True)
    oauth_blog = models.CharField('blog', max_length=200, null=True, blank=True)
    oauth_ext = models.TextField('完整信息', default='', null=True, blank=True)

    avatar = models.CharField('头像', max_length=200, default='', null=True, blank=True)

    status = models.CharField('状态', max_length=20, choices=(
        ('active', '激活'),
        ('close', '关闭，下线'),
    ), default='active')

    level = models.IntegerField("等级", choices=(
        (1, '默认'),
        (10, '初级捐赠'),
        (20, '高级捐赠'),
    ), default=1, null=True, blank=True)

    ctime = models.DateTimeField('创建时间', auto_now_add=True)
    mtime = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注', default='', null=True, blank=True)


class UserArticle(models.Model):
    """
    用户收藏文章表
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    uindex = models.IntegerField('地址')
    title = models.CharField('标题', max_length=200)
    author = models.CharField('作者', max_length=100, null=True, blank=True)
    src_url = models.CharField('原始链接', max_length=1024)

    ctime = models.DateTimeField('创建时间', auto_now_add=True)


class Message(models.Model):
    """
    留言表，是否登录用户都可以留言
    """
    uid = models.CharField('用户id', max_length=100)
    content = models.TextField('内容')
    nickname = models.CharField('用户昵称', max_length=20, null=True, blank=True)
    contact = models.CharField('用户联系方式', max_length=50, null=True, blank=True)

    status = models.CharField('状态', max_length=20, choices=(
        ('active', '激活'),
        ('close', '关闭，下线'),
    ), default='active')
    reply = models.TextField('回复', null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    ctime = models.DateTimeField('创建时间', auto_now_add=True)
    mtime = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注', default='', null=True, blank=True)


class Job(models.Model):
    """
    远程任务表，用于执行公众号任务
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    url = models.CharField('原始链接', max_length=1024)
    action = models.IntegerField('链接类型', choices=(
        (10, 'RSS 源'),
        (11, 'ershicimi 爬虫文章列表'),
        (12, 'wemp 爬虫文章列表'),
        (13, 'chuansongme 爬虫文章列表'),

        (20, 'mpwx 文章详情'),
        (21, 'ershicimi 爬虫文章详情'),
        (22, 'wemp 爬虫文章详情'),
        (23, 'chuansongme 爬虫文章详情'),
    ))
    rsp = models.TextField('内容', default='', null=True, blank=True)

    status = models.IntegerField('状态', choices=(
        (0, '待处理'),
        (1, '处理中'),
        (2, '处理成功'),
        (3, '超时'),
        (4, '解析异常'),
        (5, '交还次数超限'),
    ), default=0, db_index=True)

    dvc_id = models.CharField('设备号', max_length=128, null=True, blank=True)
    dvc_type = models.CharField('设备身份', max_length=16, choices=(
        ('user', '用户'),
        ('robot', '机器人'),
    ), null=True, blank=True)
    dvc_ip = models.CharField('设备IP', max_length=64, null=True, blank=True)
    dvc_ext = models.TextField('设备额外信息', default='', null=True, blank=True)

    giveback = models.IntegerField('交还次数', default=0)

    ctime = models.DateTimeField('创建时间', auto_now_add=True)
    mtime = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注', default='', null=True, blank=True)

