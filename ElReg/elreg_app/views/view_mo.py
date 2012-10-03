#coding: utf-8

from django.shortcuts import render_to_response
from elreg_app.models import Region
from ElReg.settings import redis_db, client

def index(request, template_name):
    """
    Логика страницы МО
    """
    id = '%s' % request.session.session_key
    print id, "<<<<<<<<<<--sessionid"
    redis_db.hset(id, 'step', 1)
#    s = request.COOKIES['sessionid']
#    print s, "<-------"

    region_list = Region.objects.filter(activation=True)
    return render_to_response(template_name, {'region_list': region_list,
                                              'step': int(redis_db.hget(id, 'step'))})