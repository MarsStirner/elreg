#coding: utf-8

from django.http import HttpResponse, Http404
from ElReg.settings import redis_db, client
import json

def index(request):
    """ Логика страницы updates
    Страница создана только для динамической подгрузки данных при помощи AJAX'а.
    Вызывается на вкладке "Подразделение/Специализация/Врач".
    Запуск через адресную строку приведет к ошибке 404.
    """
    id = '%s' % request.session.session_key
    try:
        y = client("list").service.listDoctors()
    except:
        y = ''
    tmp, new = [], {}

    if 'clickSpec' in request.GET:
        spec = request.GET['clickSpec']
        redis_db.hset(id, 'spec', spec)
        for i in y.doctors:
            if i.hospitalUid == "%s/%s"%(redis_db.hget(id, 'podrazd'), spec):
                tmp.append(i.speciality)
                tmp = list(set(tmp))
        new = dict(zip(xrange(len(tmp)), tmp))

    elif 'clickProf' in request.GET:
        prof = request.GET['clickProf']
        hospital_Uid = "%s/%s"%(redis_db.hget(id, 'podrazd'), redis_db.hget(id, 'spec'))
        for i in y.doctors:
            if i.hospitalUid == hospital_Uid and i.speciality == prof:
                tmp.append(i)
        for i in tmp:
            new[i.uid] = '%s %s %s' % (i.name.lastName, i.name.firstName, i.name.patronymic)
    else:
        raise Http404
    # создание ответа в формате json:
    response = HttpResponse()
    response['Content_Type'] = "text/javascript"
    response.write(json.dumps(new))
    return response
