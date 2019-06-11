from django.contrib import admin

from .models import *


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Site._meta.get_fields() if field.name not in ('curl_cmd', 'rsp_str')]
    list_per_page = 50
