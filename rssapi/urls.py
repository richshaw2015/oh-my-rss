from django.urls import path

from . import views_html, views_api

urlpatterns = [
    path('', views_html.index, name='index'),
    path('api/article', views_api.get_article_detail, name='get_article_detail'),
    path('api/feeds', views_api.get_feeds_html, name='get_feeds_html'),
    path('api/settings', views_api.get_settings_html, name='get_settings_html'),
    path('api/issues', views_api.get_issues_html, name='get_issues_html'),
]
