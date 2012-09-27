#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from elreg_app.models import Region
from ElReg.settings import redis_db, client_info, client_list

def index(request, template_name, okato='not'):
    """
    Логика страниц МО и ЛПУ
    """
    hospitals_list = []
    if okato == '0':
        try:
            okato = redis_db.get('okato')
            hospitals_list = client_list.service.listHospitals(ocatoCode=okato).hospitals
        except:
            hospitals_list = ''
        redis_db.set('step', 2)
    elif okato == 'not':
        try:
            info = client_info.service.getHospitalInfo()
        except:
            info = ''
        for x in range(len(info)):
            hospitals_list.append(info[x])
        redis_db.set('step', 1)
    else:
        try:
            hospitals_list = client_list.service.listHospitals(ocatoCode=okato).hospitals
        except:
            hospitals_list = ''
        redis_db.set('step', 2)
    current_region = '' if okato == 'not' else Region.objects.get(code=okato)
    region_list = Region.objects.filter(activation=True)
    redis_db.set('okato', okato)
    redis_db.set('current_region', current_region)
    return render_to_response(template_name, {'hospitals_list': hospitals_list,
                                              'region_list': region_list,
                                              'current_region': current_region,
                                              'step': redis_db.get('step')})