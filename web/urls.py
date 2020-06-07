from django.urls import path
from . import views_index, views_html, views_api, views_dash, views_oauth, views_search
from .feeds import SiteFeed

urlpatterns = [
    # public urls
    path('', views_index.index, name='index'),

    path('post/<int:id>', views_search.article, name='article'),
    path('p/<int:id>', views_search.article, name='article_short_url'),

    path('feed/<name>', SiteFeed(), name='get_feed_entries'),
    path('dash', views_dash.dashboard, name='dashboard'),
    path('dash/logs', views_dash.get_warn_log, name='get_warn_log'),

    path('robots.txt', views_search.robots, name='robots'),
    path('sitemap.txt', views_search.sitemap, name='sitemap'),
    path('search', views_search.insite_search, name='insite_search'),

    path('oauth/github/redirect', views_oauth.github_callback, name='github_callback'),

    # private urls
    path('api/html/article/detail', views_html.get_article_detail, name='get_article_detail'),
    path('api/html/feeds/all', views_html.get_all_feeds, name='get_all_feeds'),
    path('api/html/recommend/articles', views_html.get_recommend_articles, name='get_recommend_articles'),
    path('api/html/homepage/intro', views_html.get_homepage_intro, name='get_homepage_intro'),
    path('api/html/faq', views_html.get_faq, name='get_faq'),
    path('api/html/explore', views_html.get_explore, name='get_explore'),
    path('api/html/recent/sites', views_html.get_recent_sites, name='get_recent_sites'),
    path('api/html/recent/articles', views_html.get_recent_articles, name='get_recent_articles'),
    path('api/html/feed/ranking', views_html.get_feed_ranking, name='get_feed_ranking'),
    path('api/html/homepage/tips', views_html.get_homepage_tips, name='get_homepage_tips'),
    path('api/html/issues/all', views_html.get_all_issues, name='get_all_issues'),
    path('api/html/articles/list', views_html.get_article_update_view, name='get_article_update_view'),
    path('api/html/articles/list2', views_html.get_site_article_update_view, name='get_site_article_update_view'),
    path('api/html/sites/list', views_html.get_site_update_view, name='get_site_update_view'),

    path('api/dashboard/uv', views_dash.get_uv_chart_data, name='get_uv_chart_data'),
    path('api/dashboard/refer/pie', views_dash.get_refer_pie_data, name='get_refer_pie_data'),
    path('api/dashboard/refer/pv', views_dash.get_refer_pv_chart_data, name='get_refer_uv_chart_data'),
    path('api/dashboard/api/profile', views_dash.get_api_profile_chart_data, name='get_api_profile_chart_data'),

    path('api/dashboard/fix/redis/ttl', views_dash.fix_redis_ttl, name='fix_redis_ttl'),

    path('api/lastweek/articles', views_api.get_lastweek_articles, name='get_lastweek_articles'),
    path('api/actionlog/add', views_api.add_view_stats, name='add_view_stats'),
    path('api/star/article', views_api.user_star_article, name='user_star_article'),
    path('api/message/add', views_api.leave_a_message, name='leave_a_message'),
    path('api/mark/read', views_api.user_mark_read_all, name='user_mark_read_all'),
    path('api/mark/read/site', views_api.user_mark_read_site, name='user_mark_read_site'),
    path('api/update/site', views_api.user_force_update_site, name='user_force_update_site'),

    path('api/feed/add', views_api.submit_a_feed, name='submit_a_feed'),
    path('api/feed/subscribe', views_api.user_subscribe_feed, name='user_subscribe_feed'),
    path('api/feed/unsubscribe', views_api.user_unsubscribe_feed, name='user_unsubscribe_feed'),
]
