from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from models import Region


class RegionAdmin(admin.ModelAdmin):
    list_display = ('region', 'code', 'activation')
    search_fields = ('region', 'code')

admin.site.register(Region, RegionAdmin)