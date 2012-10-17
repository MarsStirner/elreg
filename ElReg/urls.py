from django.conf.urls import patterns, include, url
from django.contrib import admin
from settings import APP_NAME
admin.autodiscover()
urlpatterns = patterns('',
    # admin:
    url(r'^admin/', include(admin.site.urls)),
    # electronic regisrtature application:
    url(r'^', include(APP_NAME + '.urls')),
    )
