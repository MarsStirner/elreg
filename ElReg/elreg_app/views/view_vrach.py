#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from ElReg.settings import redis_db, client_list

def index(request, template_name):
    try:
        y = client_list.service.listDoctors()
    except:
        y = ''
    current_podrazd = redis_db.get('current_podrazd')
    prof = request.GET['prof'] if 'prof' in request.GET else redis_db.get('prof') # Исправить концовку
    doc = []
    for i in y.doctors:
        if i.hospitalUid == "%s/%s"%(redis_db.get('podrazd'), redis_db.get('spec')) and i.speciality == prof:
            doc.append(i.name)
    redis_db.set('prof', prof)
    redis_db.set('step', 5)
    return render_to_response(template_name, {'current_podrazd': current_podrazd,
                                              'prof': prof,
                                              'doc': doc,
                                              'step': redis_db.get('step')})