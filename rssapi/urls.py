from django.urls import path

from . import views_html

urlpatterns = [
    path('', views_html.index, name='index'),
]
