# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from settings import APP_NAME

urlpatterns = patterns(APP_NAME + '.views',
    # страницы сайта:
    url(r'^$', 'indexPage', {'templateName': 'mo.html'}, name="mo"),
    url(r'^medical_institution/$', 'medicalInstitutionPage', {'templateName': 'lpu.html'}, name="lpu"),
    url(r'^medical_institution/(?P<okato>\d{11}|search)/$', 'medicalInstitutionPage', {'templateName': 'lpu.html'}),
    url(r'^subdivision/$', 'subdivisionPage', {'templateName': 'podrazdelenie.html'}, name="podrazdelenie"),
    url(r'^subdivision/(?P<sub>\d{1,2})/$', 'subdivisionPage', {'templateName': 'podrazdelenie.html'}),
    url(r'^time/$', 'timePage', {'templateName': 'vremya.html'}, name="vremya"),
    url(r'^time/(?P<vremya>\d{2,3}|next|prev)/$', 'timePage', {'templateName': 'vremya.html'}),
    url(r'^patient/$', 'patientPage', {'templateName': 'pacient.html'}, name="pacient"),
    url(r'^register/$', 'registerPage', {'templateName': 'zapis.html'}, name="zapis"),
    # адреса, используемые только AJAX'ом:
    url(r'^search/$', 'searchPage'),
    url(r'^updates/$', 'updatesPage'),
)
