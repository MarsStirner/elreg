#coding: utf-8

from django.http import HttpResponse, Http404
from ElReg.settings import redis_db, client
import json

def index(request):
    """ Логика страницы search
    Страница создана только для динамической подгрузки данных при помощи AJAX'а.
    Вызывается на вкладке "ЛПУ".
    Запуск через адресную строку приведет к ошибке 404.
    """
    if request.method == 'GET':
        GET = request.GET
        new = {}
        print GET.items(), "<<<<<<"

#        try:
#            hospitals_list = client("list").service.listHospitals(ocatoCode=okato).hospitals
#        except:
#            hospitals_list = []

        # Добавить реализацию 404 ошибки !!!

        if GET.has_key('search'):
            search = request.GET.get( 'search' )
            new[1] = search
        response = HttpResponse()
        response['Content_Type'] = "text/javascript"
        response.write(json.dumps(new))
        return response

#    id = '%s' % request.session.session_key
#    try:
#        y = client("list").service.listDoctors()
#    except:
#        y = ''
#    tmp, new = [], {}
#
#    if 'clickSpec' in request.GET:
#        spec = request.GET['clickSpec']
#        redis_db.hset(id, 'spec', spec)
#        for i in y.doctors:
#            if i.hospitalUid == "%s/%s"%(redis_db.hget(id, 'podrazd'), spec):
#                tmp.append(i.speciality)
#                tmp = list(set(tmp))
#        new = dict(zip(xrange(len(tmp)), tmp))
#
#    elif 'clickProf' in request.GET:
#        prof = request.GET['clickProf']
#        hospital_Uid = "%s/%s"%(redis_db.hget(id, 'podrazd'), redis_db.hget(id, 'spec'))
#        for i in y.doctors:
#            if i.hospitalUid == hospital_Uid and i.speciality == prof:
#                tmp.append(i)
#        for i in tmp:
#            new[i.uid] = '%s %s %s' % (i.name.lastName, i.name.firstName, i.name.patronymic)
#    else:
#        raise Http404
        # создание ответа в формате json:
#    new = {1:"qw", 2:"er", 3:"ty"}
#    response = HttpResponse()
#    response['Content_Type'] = "text/javascript"
##    response.write(json.dumps(new))
#    response.write({query:'Li',suggestions:['Liberia','Libyan Arab Jamahiriya','Liechtenstein','Lithuania'],data:['LR','LY','LI','LT']})
#    return response
