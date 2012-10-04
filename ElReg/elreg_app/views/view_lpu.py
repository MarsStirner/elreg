#coding: utf-8

from django.shortcuts import render_to_response
from elreg_app.models import Region
from ElReg.settings import redis_db, client

def index(request, template_name, okato=0):
    """
    Логика страницы ЛПУ
    """
    id = '%s' % request.session.session_key
    if okato == "search":
        redis_db.hset(id, 'step', 2)
        return render_to_response(template_name, {
                                                  'step': int(redis_db.hget(id, 'step'))})
    else:
        if not okato:
            okato = redis_db.hget(id, 'okato')
        try:
            hospitals_list = client("list").service.listHospitals(ocatoCode=okato).hospitals
        except:
            hospitals_list = []
        current_region = Region.objects.get(code=okato)
        redis_db.hset(id, 'current_region', current_region)
        redis_db.hset(id, 'okato', okato)
        redis_db.hset(id, 'step', 2)
        return render_to_response(template_name, {'hospitals_list': hospitals_list,
                                                  'current_region': current_region,
                                                  'step': int(redis_db.hget(id, 'step'))})