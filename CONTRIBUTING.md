## 代码导读

本项目有 django 工程和 scrapy 工程组成，工程目录结构如下：

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
├── feed  scrapy工程
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
├── scrapy.cfg  scrapy工程配置
├── assets  前端的静态文件，包括图片、脚本、样式、字体等
└── requirements.txt  依赖库声明
```

## 如何增加自定义爬虫
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

提交该文件后，系统会根据定时任务（day、week、month）配置自动爬取文章内容并入库。

注意：爬虫站点的内容必须为优质。

## 前端文件的处理？
前端的处理是另外一个工程，采用 JQuery 构建，由于代码比较乱，暂时只放置构建后的代码，后续视情况再考虑。

## 更多
欢迎Issue、PR或加群讨论。
