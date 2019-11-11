from django.urls import path

from . import views_index, views_html, views_api, views_dash

urlpatterns = [
    path('', views_index.index, name='index'),
    path('post/<int:uindex>', views_index.article, name='article'),

    path('api/html/article/detail', views_html.get_article_detail, name='get_article_detail'),
    path('api/html/feeds/all', views_html.get_all_feeds, name='get_all_feeds'),
    path('api/html/homepage/intro', views_html.get_homepage_intro, name='get_homepage_intro'),
    path('api/html/faq', views_html.get_faq, name='get_faq'),
    path('api/html/homepage/tips', views_html.get_homepage_tips, name='get_homepage_tips'),
    path('api/html/issues/all', views_html.get_all_issues, name='get_all_issues'),
    path('api/html/articles/list', views_html.get_articles_list, name='get_articles_list'),

    path('api/dashboard/uv', views_dash.get_uv_chart_data, name='get_uv_chart_data'),
    path('api/dashboard/refer/pie', views_dash.get_refer_pie_data, name='get_refer_pie_data'),
    path('api/dashboard/refer/pv', views_dash.get_refer_pv_chart_data, name='get_refer_uv_chart_data'),

    path('dash', views_dash.dashboard, name='dashboard'),

    path('api/lastweek/articles', views_api.get_lastweek_articles, name='get_lastweek_articles'),
    path('api/actionlog/add', views_api.add_log_action, name='add_log_action'),
    path('api/message/add', views_api.leave_a_message, name='leave_a_message'),
    path('api/feed/add', views_api.submit_a_feed, name='submit_a_feed'),

    path('robots.txt', views_index.robots, name='robots'),
    path('sitemap.txt', views_index.sitemap, name='sitemap'),
]
