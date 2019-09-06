from django.contrib import admin

from .models import *


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'cname', 'author', 'link', 'favicon', 'brief', 'star', 'freq', 'status', 'ctime', 'mtime',
                    'remark', 'tag', 'copyright')
    search_fields = ('name', 'cname', 'author', 'brief')
    list_filter = ('status', 'freq', 'tag', 'copyright')
    list_per_page = 100


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Article._meta.get_fields() if field.name not in ('content', )]
    search_fields = ['title', 'content', 'src_url']
    list_filter = ('status', )
    list_per_page = 50


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Message._meta.get_fields()]
    search_fields = ['nickname', 'content', 'contact', 'remark']
    list_editable = ['reply', ]
    list_filter = ('status',)
    list_per_page = 50
