# Oh My RSS
Oh My RSS 是一个开源的在线RSS服务，通过爬虫汇聚互联网上的精华内容，旨在为国内的 IT 从业者提供一个优质的学习圈子。

![预览](https://raw.githubusercontent.com/richshaw2015/oh-my-rss/master/assets/img/preview.jpg)

## 功能特性

### 持续扩充的订阅源
为了确保内容质量，Oh My RSS 对订阅源有严格的筛选标准：
- 巨头公司的技术博客
- 技术大拿的博客
- 互联网名站的热门

 除了爬虫支持，也可以提交自定义的订阅源^o^
 
### VimLike的快捷键
Vim 党的福音来了~

<table class="responsive-table">
    <tr>
        <td><code> n </code> 下一篇文章（next）</td>
        <td><code> N </code> 上一篇文章</td>
        <td><code> F </code> 切换全屏（fullscreen）</td>
    </tr>
    <tr>
        <td><code> p </code> 下一页（page）</td>
        <td><code> P </code> 上一页</td>
        <td><code> D </code> 标记本页已读并翻页</td>
    </tr>
    <tr>
        <td><code> j </code> 向下移动一行</td>
        <td><code> k </code> 向上移动一行</td>
        <td><code> space </code> 向下翻一页</td>
    </tr>
    <tr>
        <td><code> gg </code> 回顶部</td>
        <td><code> G </code> 去底部</td>
        <td><code> f </code> 链接全览</td>
    </tr>
</table>

### 更多
欢迎Issue、PR或加群讨论。

## 快速开始
### 依赖
必须的：
- Python3
- Python3依赖库，详见 requirements.txt

可选的：
- Redis服务（6379端口），用于记录阅读数、点赞数等数据
- requirements.txt 中的依赖库 `gunicorn`、`gevent` 在开发环境为非必须
- `chromium`、`chromedriver` 只有在处理纯 js 渲染页面时才需要

### 运行Web服务

```shell
python3 manage.py runserver
```

### 数据库相关

初始化：
```shell
python3 manage.py makemigrations web 
python3 manage.py migrate
```

数据录入：

在 django 管理后台录入站点信息，或者在线提交订阅源地址。

### 爬虫
运行爬虫采集命令，例如：
```shell
scrapy crawl coolshell
```

提交的订阅源会以每小时一次的频率更新。

## 贡献
详见 CONTRIBUTING.md

## 交流群
请扫码加群，备注 `RSS` 或加入我们的[Slack社区](https://ohmyrss.slack.com/)

![预览](https://raw.githubusercontent.com/richshaw2015/oh-my-rss/master/assets/img/qrcode.jpg)
