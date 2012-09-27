#coding: utf-8

from django.contrib import admin
from models import Region


class RegionAdmin(admin.ModelAdmin):
    """
    Класс, добавляющий в админку возможность добавлять (изменять, удалять) название МО и его код ОКАТО
    """
    list_display = ('region', 'code', 'activation')
    search_fields = ('region', 'code')

admin.site.register(Region, RegionAdmin)