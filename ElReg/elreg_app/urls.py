from django.conf.urls import patterns, url
from settings import APP_NAME

urlpatterns = patterns(APP_NAME + '.views',
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