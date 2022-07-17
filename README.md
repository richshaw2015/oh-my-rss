# 己思
己思是一个开源的 RSS 体验站，旨在探索更加高效阅读的可能。

![预览](https://raw.githubusercontent.com/richshaw2015/oh-my-rss/master/assets/img/preview.jpg)

## 功能特性

### 持续扩充的订阅源

一些支持的订阅源：

`酷 壳 – CoolShell` 、  `科技爱好者周刊` 、  `GitHub 热门` 、  `有赞技术团队` 、  `... `

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

### 关于
本站仅为演示用，完整功能请下载桌面客户端 [Dinosaur Rss 🦕](https://dinorss.org/)

## 快速开始
### 依赖
必须的：
- Python3
- Python3依赖库，详见 requirements.txt

可选的：
- Redis服务（6379端口），用于记录阅读数、点赞数等数据
- requirements.txt 中的依赖库 `gunicorn`、`gevent` 在开发环境为非必须

### 运行Web服务

```shell
python3 manage.py runserver
```

### 数据库相关

初始化：
```shell
python3 manage.py migrate web
```

数据录入：

在 Django 管理后台录入站点信息，或者在线提交订阅源地址。

## 贡献
详见 CONTRIBUTING.md
