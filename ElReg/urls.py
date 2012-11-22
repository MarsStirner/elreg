# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from settings import APP_NAME, DEBUG
admin.autodiscover()

urlpatterns = patterns('',
    # административный интерфейс:
    url(r'^admin/settings/', include('livesettings.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # электронная регистратура:
    url(r'^', include(APP_NAME + '.urls')),
    )
