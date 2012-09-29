#coding: utf-8

from django.shortcuts import render_to_response
from django.http import Http404
from ElReg.settings import redis_db, client_list

def index(request, template_name, spec='404'):
    """
    Логика страницы Специализация
    """
    if spec == '404':
        raise Http404()
    if spec == '0':
        spec = redis_db.get('spec')
    try:
        y = client_list.service.listDoctors()
    except:
        y = ''
    spc = []
    for i in y.doctors:
        if i.hospitalUid == "%s/%s"%(redis_db.get('podrazd'), spec):
            spc.append(i.speciality)
            spc = list(set(spc))

    current_podrazd = ''

    for i in y.hospitals:
        if i.uid == "%s/%s"%(redis_db.get('podrazd'), spec):
            current_podrazd = i.title
            break
    redis_db.set('spec', spec)
    redis_db.set('current_podrazd', current_podrazd)
    redis_db.set('step', 4)
    return render_to_response(template_name, {'spc': spc,
                                              'current_podrazd': current_podrazd,
                                              'step': int(redis_db.get('step'))})