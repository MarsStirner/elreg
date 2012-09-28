#coding: utf-8

from django.shortcuts import render_to_response
from django.http import Http404
from ElReg.settings import redis_db, client_info, client_list

def index(request, template_name, podrazd='404'):
    """
    Логика страницы Подразделение
    """
    if podrazd == '404':
        raise Http404()
    if podrazd == '0':
        podrazd = redis_db.get('podrazd')
    try:
        x = client_info.service.getHospitalInfo()
    except:
        x = ''
    podrazdelenie_list = []
    for c in x:
        if c.uid.startswith('%s'%(podrazd)):
            current_lpu = c
            for b in c.buildings:
                podrazdelenie_list.append(b.title)

    new_list = []
    y = client_list.service.listHospitals().hospitals
    for v in y:
        for w in podrazdelenie_list:
            if v.uid.startswith('%s'%(podrazd)) and v.title == w:
                new_list.append(v.uid.split('/')[1])
    new = zip(podrazdelenie_list, new_list)
    redis_db.set('podrazd', podrazd)
    redis_db.set('current_lpu', current_lpu)
    redis_db.set('step', 3)
    return render_to_response(template_name, {'podrazdelenie_list': podrazdelenie_list,
                                              'current_lpu': current_lpu,
                                              'new_list': new_list,
                                              'new': new,
                                              'step': redis_db.get('step')})