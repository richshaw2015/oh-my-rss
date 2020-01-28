## 1. 代码导读

本项目有 django、scrapy、gulp 等工程组成，工程目录结构如下：

```
├── README.md  项目介绍
├── CONTRIBUTING.md  贡献指南
├── LICENSE  授权协议
├── ohmyrss  django工程配置
├── web  django应用
│   ├── admin.py  管理后台
│   ├── apps.py
│   ├── models.py  模型定义
│   ├── tests.py
│   ├── urls.py  路由定义
│   ├── utils.py  自己封装的工具方法
│   ├── verify.py  通用的请求参数校验装饰器
│   ├── cron.py  定时任务
│   ├── view_api.py  api请求的控制器
│   ├── views_html.py  html请求的控制器
│   └── views_index.py  首页请求的控制器
├── tmpl  django工程模板
├── manage.py  django的管理入口
├── src  前端工程源码，构建生成的文件输出到 assets 目录
│   ├── js
│   ├── css
│   ├── font
├── feed  scrapy 工程
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── run.py  调试用
│   ├── settings.py  scrapy应用配置
│   ├── utils.py  爬虫用的工具方法
│   ├── spiders  爬虫文件
│   │   ├── day  以天为单位进行的爬虫
│   │   ├── week  以周为单位进行的爬虫
│   │   ├── month  以月为单位进行的爬虫
│   │   └── spider.py  爬虫实现父类
├── scrapy.cfg  scrapy 工程配置
├── assets  前端的静态文件，包括图片、脚本、样式、字体等，gulp 构建会覆盖其中的文件
├── gulpfile.js  前端构建规则
├── package.json 前端构建工程的开发依赖
├── package-lock.js  前端依赖包
└── requirements.txt  python3 依赖库声明
```

## 2. 如何增加自定义 scrapy 爬虫
根据目标站点的更新频率，在对应目录（day、week、month）下新建爬虫文件，例如 demo_spider.py，该文件需自定义 xpath 规则等参数，例如：

```python
class DemoSpider(Spider):
    name = 'demo'

    def __init__(self):
        Spider.__init__(self,
                        start_urls=[
                            'https://www.demo.com',
                        ],
                        index_xpath="//h2[@class='post-title']/a/@href",
                        article_title_xpath='//h1[@class="post-title"]/a/text()',
                        article_content_xpath='//div[@class="post-content"]',
                        index_limit_count=3,
                        )
```

其中 Spider 类初始化参数含义如下：
- 【必须】`start_urls` 爬虫开始地址，
- 【必须】`index_xpath` 文章链接地址，获取的是地址集合
- 【必须】`article_title_xpath` 文章标题，获取的是文本
- 【必须】`article_content_xpath` 文章内容，获取的是DOM节点
- `index_limit_count` 最多爬取的文章链接数，默认None （不限制）
- `article_trim_xpaths` 需要屏蔽的文章内容节点，获取的是DOM节点，默认None（不屏蔽）
- `browser` 是否使用浏览器爬虫，只有纯JS渲染的页面才需要，默认 False

提交该文件后，系统会根据定时任务（day、week、month）配置自动爬取文章内容并入库

注意：爬虫站点的内容必须为优质

## 3. 前端工程的处理

前端主要使用 JQuery 开发，使用 gulp 构建

### 3.1 安装前端开发依赖

需要提前安装好 node、npm 命令

```shell script
npm install
```

### 3.2 运行 gulp

生成目标文件（assets 目录）：

```shell script
gulp build
```

开发过程监控文件变化，实时生成目标文件：

```shell script
gulp
```

## 4. 运行环境安装
以 Centos 服务器为例，对相关的运行环境进行说明

### 4.1 安装系统命令

```
yum groupinstall 'Development Tools'
yum install gcc openssl-devel bzip2-devel libffi-devel
yum install telnet telnet-server
yum install sqlite-devel
```

### 4.2 安装 nginx

```shell script
yum install nginx
```
参考 https://www.cyberciti.biz/faq/how-to-install-and-use-nginx-on-centos-7-rhel-7/

注意配置静态文件的可执行权限，配置网站的配置

### 4.3 安装 python3
参考 https://tecadmin.net/install-python-3-7-on-centos/

```shell script
yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
sudo yum -y install gcc gcc-c++
sudo yum -y install zlib zlib-devel
sudo yum -y install libffi-devel
./configure --enable-optimizations --enable-loadable-sqlite-extensions
make
make install
```

### 4.4 安装及配置 centbot
用于证书的自动续期

```
yum install certbot
```

### 4.5 编译及安装 redis
下载源码，make 即可，注意修改配置文件几个项目：

```shell script
daemonize yes
maxmemory 100000000
maxmemory-policy volatile-lru
```

启动命令：
```shell script
./src/redis-server redis.conf
```

### 4.6 编译及安装 sqlite3
注意替换掉系统的 sqlite3，那个版本比较老

### 4.7 pyhton3 依赖包安装
按照 requirements.txt 安装即可

### 4.8 chromium 及 driver 环境安装
```
yum install chromium
```

安装完后要下载匹配版本的 chromedriver 放到系统 PATH 里

## 5. 更多
欢迎 Issue、PR 或加群讨论。
