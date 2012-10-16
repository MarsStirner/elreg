from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('elreg_app.views',
    # admin:
    url(r'^admin/', include(admin.site.urls)),
    # site:
    url(r'^$', 'moPage', {'template_name': 'mo.html'}, name="mo"),
    url(r'^lpu/$', 'lpuPage', {'template_name': 'lpu.html'}, name="lpu"),
    url(r'^lpu/(?P<okato>\d{11}|search)/$', 'lpuPage', {'template_name': 'lpu.html'}),
    url(r'^podrazdelenie/$', 'podrazdeleniePage', {'template_name': 'podrazdelenie.html'}, name="podrazdelenie"),
    url(r'^podrazdelenie/(?P<podrazd>\d{1,2})/$', 'podrazdeleniePage', {'template_name': 'podrazdelenie.html'}),
    url(r'^vremya/$', 'vremyaPage', {'template_name': 'vremya.html'}, name="vremya"),
    url(r'^vremya/(?P<vremya>\d{2,3}|next|prev)/$', 'vremyaPage', {'template_name': 'vremya.html'}),
    url(r'^pacient/$', 'pacientPage', {'template_name': 'pacient.html'}, name="pacient"),
    url(r'^zapis/$', 'zapisPage', {'template_name': 'zapis.html'}, name="zapis"),
    # ajax only:
    url(r'^search/$', 'searchPage'),
    url(r'^updates/$', 'updatesPage'),
    )
