# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from settings import APP_NAME, MEDIA_ROOT

urlpatterns = patterns(APP_NAME + '.views',
    # страницы сайта:
    url(r'^$', 'indexPage', {'templateName': 'index.html'}, name="index"),
    url(r'^medical_institution/$', 'medicalInstitutionPage', {'templateName': 'medical_institution.html'}, name="medical_institution"),
    url(r'^medical_institution/(?P<okato>\d{11}|search)/$', 'medicalInstitutionPage', {'templateName': 'medical_institution.html'}),
    url(r'^subdivision/$', 'subdivisionPage', {'templateName': 'subdivision.html'}, name="subdivision"),
    url(r'^subdivision/(?P<sub>\d{1,2})/$', 'subdivisionPage', {'templateName': 'subdivision.html'}),
    url(r'^time/$', 'timePage', {'templateName': 'time.html'}, name="time"),
    url(r'^time/(?P<time>\d{2,3}|next|prev)/$', 'timePage', {'templateName': 'time.html'}),
    url(r'^patient/$', 'patientPage', {'templateName': 'patient.html'}, name="patient"),
    url(r'^register/$', 'registerPage', {'templateName': 'register.html'}, name="register"),
    # адреса, используемые только AJAX'ом:
    url(r'^search/$', 'searchPage'),
    url(r'^updates/$', 'updatesPage'),
)
urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': MEDIA_ROOT,
        }),
)
