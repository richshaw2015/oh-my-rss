from django.contrib import admin

from .models import *


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'cname', 'author', 'link', 'favicon', 'brief', 'star', 'freq', 'status', 'ctime', 'mtime',
                    'remark', 'tag', 'copyright')
    list_per_page = 100


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Article._meta.get_fields() if field.name not in ('content', )]
    list_per_page = 50


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Message._meta.get_fields()]
    list_per_page = 50
