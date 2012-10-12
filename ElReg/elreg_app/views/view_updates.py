#coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from ElReg.settings import redis_db
from elreg_app.functions import ListWSDL
import json

def index(request):
    """ Логика страницы updates
    Страница создана только для динамической подгрузки данных при помощи AJAX'а.
    Вызывается на вкладке "Подразделение/Специализация/Врач".
    Запуск через адресную строку приведет к редиректу на главную страницу.
    """
    id = request.session.session_key
    doctors_list = ListWSDL().listDoctors()
    tmp, new = [], {}

    if 'clickSpec' in request.GET:
        spec = request.GET['clickSpec']
        redis_db.hset(id, 'spec', spec)
        for i in doctors_list:
            if i.hospitalUid == "%s/%s"%(redis_db.hget(id, 'podrazd'), spec):
                tmp.append(i.speciality)
                tmp = list(set(tmp))
        new = dict(zip(xrange(len(tmp)), tmp))

    elif 'clickProf' in request.GET:
        prof = request.GET['clickProf']
        hospital_Uid = "%s/%s"%(redis_db.hget(id, 'podrazd'), redis_db.hget(id, 'spec'))
        for i in doctors_list:
            if i.hospitalUid == hospital_Uid and i.speciality == prof:
                tmp.append(i)
        for i in tmp:
            new[i.uid] = '%s %s %s' % (i.name.lastName, i.name.firstName, i.name.patronymic)
    else:
        return HttpResponseRedirect("/")
    # создание ответа в формате json:
    response = HttpResponse()
    response['Content_Type'] = "text/javascript"
    response.write(json.dumps(new))
    return response
