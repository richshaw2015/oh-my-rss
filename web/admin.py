from django.contrib import admin

from .models import *


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('cname', 'author', 'link', 'star', 'status', 'ctime', 'mtime', 'tag', 'rss')
    search_fields = ('name', 'cname', 'author', 'brief', 'link', 'remark')
    list_filter = ('status', 'freq', 'tag', 'copyright', 'creator')
    list_per_page = 100


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'ctime')
    search_fields = ('title', 'content', 'src_url', 'uindex', 'remark', 'author')
    list_filter = ('status', )
    list_per_page = 50


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Message._meta.get_fields()]
    search_fields = ['nickname', 'content', 'contact', 'remark']
    list_editable = ['reply', ]
    list_filter = ('status',)
    list_per_page = 50
