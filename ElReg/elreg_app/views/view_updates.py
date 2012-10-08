#coding: utf-8

from django.http import HttpResponse
from django.core import serializers
from elreg_app.models import Region
from ElReg.settings import redis_db, client

def index(request):
    """
    Логика страницы updates
    """
    id = '%s' % request.session.session_key

    try:
        y = client("list").service.listDoctors()
    except:
        y = []
    import json


    y = json.dumps(y)
    print type(y)
    print y

    response = HttpResponse()
    response['Content_Type'] = "text/javascript"
    response.write(serializers.serialize("json", y))
    return response
