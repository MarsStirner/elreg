from django.conf.urls import patterns, include, url
from django.contrib import admin
from elreg_app.views import view_index, view_lpu
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', view_index.index, name='index'),
    url(r'^lpu/(\d{10,11})/$', view_lpu.index, name='lpu')
    # Examples:
    # url(r'^$', 'ElReg.views.home', name='home'),
    # url(r'^ElReg/', include('ElReg.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    )
