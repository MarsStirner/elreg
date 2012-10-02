#coding: utf-8

from django.shortcuts import render_to_response
from elreg_app.models import Region
from ElReg.settings import redis_db

def index(request, template_name):
    """
    Логика страницы МО
    """
    redis_db.set('step', 1)
    id = '%s' % request.session.session_key
    dic = {'step': 1}
    redis_db.set(id, dic)
    dic = redis_db.get(id)['a']=134
    redis_db.set(id, dic)

    region_list = Region.objects.filter(activation=True)
    return render_to_response(template_name, {'region_list': region_list,
                                              'step': int(redis_db.get('step'))})