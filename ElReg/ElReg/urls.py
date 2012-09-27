from django.conf.urls import patterns, include, url
from django.contrib import admin
from elreg_app.views import view_lpu, view_podrazdelenie, view_specializaciya, view_vrach, view_vremya
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', view_lpu.index, {'template_name': 'index.html'}, name="index"),
    url(r'^lpu/(?P<okato>0|\d{11})/$', view_lpu.index, {'template_name': 'lpu.html'}, name="lpu"),
    url(r'^podrazdelenie/(?P<podrazd>\d{1,2})/$', view_podrazdelenie.index, {'template_name': 'podrazdelenie.html'}, name="podrazdelenie"),
    url(r'^specializaciya/(?P<spec>\d{1,13})/$', view_specializaciya.index, {'template_name': 'specializaciya.html'}, name="specializaciya"),
    url(r'^vrach/$', view_vrach.index, {'template_name': 'vrach.html'}, name="vrach"),
    url(r'^vremya/(?P<vremya>\d{2,3})/$', view_vremya.index, {'template_name': 'vremya.html'}, name="vremya"),

    # Examples:
    # url(r'^$', 'ElReg.views.home', name='home'),
    # url(r'^ElReg/', include('ElReg.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    )
