from django.conf.urls import patterns, url
from settings import APP_NAME

urlpatterns = patterns(APP_NAME + '.views',
    # site:
    url(r'^$', 'moPage', {'template_name': 'mo.html'}, name="mo"),
    url(r'^medical_institution/$', 'lpuPage', {'template_name': 'lpu.html'}, name="lpu"),
    url(r'^medical_institution/(?P<okato>\d{11}|search)/$', 'lpuPage', {'template_name': 'lpu.html'}),
    url(r'^subdivision/$', 'podrazdeleniePage', {'template_name': 'podrazdelenie.html'}, name="podrazdelenie"),
    url(r'^subdivision/(?P<podrazd>\d{1,2})/$', 'podrazdeleniePage', {'template_name': 'podrazdelenie.html'}),
    url(r'^time/$', 'vremyaPage', {'template_name': 'vremya.html'}, name="vremya"),
    url(r'^time/(?P<vremya>\d{2,3}|next|prev)/$', 'vremyaPage', {'template_name': 'vremya.html'}),
    url(r'^patient/$', 'pacientPage', {'template_name': 'pacient.html'}, name="pacient"),
    url(r'^register/$', 'zapisPage', {'template_name': 'zapis.html'}, name="zapis"),
    # ajax only:
    url(r'^search/$', 'searchPage'),
    url(r'^updates/$', 'updatesPage'),
)