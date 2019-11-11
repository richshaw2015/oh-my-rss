from django.contrib import admin
from django.utils.safestring import mark_safe
from django.forms import TextInput, Textarea
from .models import *


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    def view_link(self):
        return mark_safe(f"<a href='{self.link}' target='_blank'>{self.link[:20]}</a>")
    view_link.short_description = ''

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 20})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 20})},
    }

    list_display = ('cname', 'author', view_link, 'star', 'remark', 'favicon', 'ctime', 'tag', 'rss')
    search_fields = ('name', 'cname', 'author', 'brief', 'link', 'remark')
    list_filter = ('status', 'freq', 'copyright', 'creator')
    list_editable = ['star', 'author', 'remark', 'tag', 'favicon']
    list_per_page = 6


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'ctime')
    search_fields = ('title', 'content', 'src_url', 'uindex', 'remark', 'author')
    list_filter = ('status', )
    list_per_page = 50


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '10'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 20})},
    }

    list_display = [field.name for field in Message._meta.get_fields()]
    search_fields = ['nickname', 'content', 'contact', 'remark']
    list_editable = ['reply', ]
    list_filter = ('status',)
    list_per_page = 50
