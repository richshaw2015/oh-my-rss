from django.urls import path

from . import views_html, views_api, views_ajax

urlpatterns = [
    path('', views_html.index, name='index'),
    path('api/html/article', views_api.get_article_detail, name='get_article_detail'),
    path('api/html/feeds', views_api.get_feeds_html, name='get_feeds_html'),
    path('api/html/homepage', views_api.get_homepage_html, name='get_homepage_html'),
    path('api/html/issues', views_api.get_issues_html, name='get_issues_html'),

    path('api/ajax/myarticles', views_ajax.get_my_article_list, name='get_my_article_list'),
    path('api/ajax/mytoreads', views_ajax.get_my_lastweek_articles, name='get_my_lastweek_articles'),
    path('api/ajax/actionlog', views_ajax.log_action, name='log_action'),
    path('api/ajax/leavemsg', views_ajax.leave_a_message, name='leave_a_message'),
]
