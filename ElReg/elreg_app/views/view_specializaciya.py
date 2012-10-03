#coding: utf-8

from django.shortcuts import render_to_response
from django.http import Http404
from ElReg.settings import redis_db, client

def index(request, template_name, spec=0):
    """
    Логика страницы Специализация
    """
    id = '%s' % request.session.session_key
    if not spec:
        spec = redis_db.hget(id, 'spec')
    try:
        y = client("list").service.listDoctors()
    except:
        y = []
    spc = []
    for i in y.doctors:
        if i.hospitalUid == "%s/%s"%(redis_db.hget(id, 'podrazd'), spec):
            spc.append(i.speciality)
            spc = list(set(spc))

    current_podrazd = ''

    for i in y.hospitals:
        if i.uid == "%s/%s"%(redis_db.hget(id, 'podrazd'), spec):
            current_podrazd = i.title
            break
    redis_db.hset(id, 'spec', spec)
    redis_db.hset(id, 'current_podrazd', current_podrazd)
    redis_db.hset(id, 'step', 4)
    return render_to_response(template_name, {'spc': spc,
                                              'current_podrazd': current_podrazd,
                                              'step': int(redis_db.hget(id, 'step'))})