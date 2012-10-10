#coding: utf-8

from django.shortcuts import render_to_response
from ElReg.settings import redis_db, client

def index(request, template_name):
    """Логика страницы Врач
    ДОБАВИТЬ описание
    """
    id = '%s' % request.session.session_key
    try:
        y = client("list").service.listDoctors()
    except:
        y = ''
    current_podrazd = redis_db.hget(id, 'current_podrazd')
    prof = request.GET['prof'] if 'prof' in request.GET else redis_db.hget(id, 'prof').decode('utf-8') # decode для случая если получаем str, что не допустимо
    doc = []
    hospital_Uid = "%s/%s"%(redis_db.hget(id, 'podrazd'), redis_db.hget(id, 'spec'))
    for i in y.doctors:
        if i.hospitalUid == hospital_Uid and i.speciality == prof:
            doc.append(i)
    redis_db.hset(id, 'hospital_Uid', hospital_Uid)
    redis_db.hset(id, 'prof', prof)
    redis_db.hset(id, 'step', 5)
    return render_to_response(template_name, {'current_podrazd': current_podrazd,
                                              'prof': prof,
                                              'doc': doc,
                                              'step': int(redis_db.hget(id, 'step'))})