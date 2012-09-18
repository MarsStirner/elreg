from django.conf.urls import patterns, include, url
from elreg_app.views import view_index, view_lpu_regions
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', view_index.index),
    url(r'^lpu-regions/$', view_lpu_regions.index),
    # Examples:
    # url(r'^$', 'ElReg.views.home', name='home'),
    # url(r'^ElReg/', include('ElReg.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    )
