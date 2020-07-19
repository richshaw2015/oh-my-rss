from django.urls import path
from web.views import dashboard, install, index, search, views_api, views_html, oauth
from web.feeds import SiteFeed

urlpatterns = [
    # public urls
    path('', index.index, name='index'),

    path('post/<int:pid>', search.article, name='article'),
    path('p/<int:pid>', search.article, name='article_alias'),

    path('feed/<site_id>', SiteFeed(), name='get_feed_entries'),
    path('dash', dashboard.dashboard, name='dashboard'),
    path('dash/logs', dashboard.get_warn_log, name='get_warn_log'),

    path('robots.txt', search.robots, name='robots'),
    path('sitemap.txt', search.sitemap, name='sitemap'),
    path('search', search.in_site_search, name='in_site_search'),

    path('oauth/github/redirect', oauth.github_callback, name='github_callback'),

    # private urls
    path('api/html/article/detail', views_html.get_article_detail, name='get_article_detail'),
    path('api/html/feeds/all', views_html.get_my_feeds, name='get_my_feeds'),
    path('api/html/recommend/articles', views_html.get_recommend_articles, name='get_recommend_articles'),
    path('api/html/homepage/intro', views_html.get_homepage_intro, name='get_homepage_intro'),
    path('api/html/faq', views_html.get_faq, name='get_faq'),
    path('api/html/explore', views_html.get_explore, name='get_explore'),
    path('api/html/recent/sites', views_html.get_recent_sites, name='get_recent_sites'),
    path('api/html/recent/articles', views_html.get_recent_articles, name='get_recent_articles'),
    path('api/html/ranking', views_html.get_ranking, name='get_ranking'),
    path('api/html/feed/ranking', views_html.get_feed_ranking, name='get_feed_ranking'),
    path('api/html/user/ranking', views_html.get_user_ranking, name='get_user_ranking'),
    path('api/html/donate', views_html.get_donate_guide, name='get_donate_guide'),
    path('api/html/issues/all', views_html.get_all_issues, name='get_all_issues'),
    path('api/html/articles/list', views_html.get_article_update_view, name='get_article_update_view'),
    path('api/html/articles/list2', views_html.get_site_article_update_view, name='get_site_article_update_view'),
    path('api/html/sites/list', views_html.get_site_update_view, name='get_site_update_view'),

    path('api/dashboard/uv', dashboard.get_uv_chart_data, name='get_uv_chart_data'),
    path('api/dashboard/refer/pie', dashboard.get_refer_pie_data, name='get_refer_pie_data'),
    path('api/dashboard/refer/pv', dashboard.get_refer_pv_chart_data, name='get_refer_uv_chart_data'),
    path('api/dashboard/api/profile', dashboard.get_api_profile_chart_data, name='get_api_profile_chart_data'),

    path('api/install', install.install, name='install'),
    path('api/load', install.load_db_data, name='load'),
    path('api/debug', install.debug, name='debug'),

    path('api/lastweek/articles', views_api.get_lastweek_articles, name='get_lastweek_articles'),
    path('api/actionlog/add', views_api.add_view_stats, name='add_view_stats'),
    path('api/star/article', views_api.user_star_article, name='user_star_article'),
    path('api/message/add', views_api.leave_a_message, name='leave_a_message'),
    path('api/mark/read', views_api.user_mark_read_all, name='user_mark_read_all'),
    path('api/update/site', views_api.user_force_update_site, name='user_force_update_site'),

    path('api/feed/add', views_api.submit_a_feed, name='submit_a_feed'),
    path('api/feed/subscribe', views_api.user_subscribe_feed, name='user_subscribe_feed'),
    path('api/feed/unsubscribe', views_api.user_unsubscribe_feed, name='user_unsubscribe_feed'),
]
