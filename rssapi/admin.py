from django.contrib import admin

from .models import *


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'cname', 'author', 'link', 'favico', 'brief', 'star', 'freq', 'status', 'ctime', 'mtime',
                    'remark')
    list_per_page = 50


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Article._meta.get_fields()]
    list_per_page = 50
