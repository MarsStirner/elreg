from django.conf.urls import patterns, include, url
from django.contrib import admin
from elreg_app.views import view_mo, view_lpu, view_podrazdelenie, view_specializaciya, view_vrach, view_vremya, view_pacient, view_zapis, view_updates, view_search
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', view_mo.index, {'template_name': 'mo.html'}, name="mo"),
    url(r'^updates/$', view_updates.index),
    url(r'^search/$', view_search.index),
    url(r'^lpu/$', view_lpu.index, {'template_name': 'lpu.html'}, name="lpu"),
    url(r'^lpu/(?P<okato>\d{11}|search)/$', view_lpu.index, {'template_name': 'lpu.html'}),
    url(r'^podrazdelenie/$', view_podrazdelenie.index, {'template_name': 'podrazdelenie.html'}, name="podrazdelenie"),
    url(r'^podrazdelenie/(?P<podrazd>\d{1,2})/$', view_podrazdelenie.index, {'template_name': 'podrazdelenie.html'}),
    url(r'^specializaciya/$', view_specializaciya.index, {'template_name': 'specializaciya.html'}, name="specializaciya"),
    url(r'^specializaciya/(?P<spec>\d{2,13})/$', view_specializaciya.index, {'template_name': 'specializaciya.html'}),
    url(r'^vrach/$', view_vrach.index, {'template_name': 'vrach.html'}, name="vrach"),
    url(r'^vremya/$', view_vremya.index, {'template_name': 'vremya.html'}, name="vremya"),
    url(r'^vremya/(?P<vremya>\d{2,3}|next|prev)/$', view_vremya.index, {'template_name': 'vremya.html'}),
    url(r'^pacient/$', view_pacient.index, {'template_name': 'pacient.html'}, name="pacient"),
    url(r'^zapis/$', view_zapis.index, {'template_name': 'zapis.html'}, name="zapis"),

    # Examples:
    # url(r'^$', 'ElReg.views.home', name='home'),
    # url(r'^ElReg/', include('ElReg.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    )
