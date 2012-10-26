# -*- coding: utf-8 -*-

from django.contrib import admin
from models import Region

class RegionAdmin(admin.ModelAdmin):
    """Класс, добавляющий регионы в админку
    Класс дает возможность добавлять (изменять, удалять) название МО и его код ОКАТО в административный интерфейс.

    """
    list_display = ('region', 'code', 'activation')
    search_fields = ('region', 'code')

admin.site.register(Region, RegionAdmin)