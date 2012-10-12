#coding: utf-8

from django.shortcuts import render_to_response
from ElReg.settings import redis_db
from elreg_app.functions import InfoWSDL, ListWSDL

def index(request, template_name, podrazd=0):
    """Логика страницы Подразделение/Специализация/Врач
    Логика страницы Подразделение
    """

    id = '%s' % request.session.session_key
    if not podrazd:
        podrazd = redis_db.hget(id, 'podrazd')
    info_list = InfoWSDL().getHospitalInfo()
    podrazdelenie_list = []
    current_lpu = ''
    for c in info_list:
        if c.uid.startswith('%s'%(podrazd)):
            current_lpu = c
            for b in c.buildings:
                podrazdelenie_list.append(b.title)

    tmp_list = []
    list_list = ListWSDL().listHospitals()
    for v in list_list:
        for w in podrazdelenie_list:
            if v.uid.startswith('%s'%(podrazd)) and v.title == w:
                tmp_list.append(v.uid.split('/')[1])
    podrazd_list = zip(podrazdelenie_list, tmp_list)
    redis_db.hset(id, 'podrazd', podrazd)
    redis_db.hset(id, 'current_lpu_title', current_lpu[1])
    redis_db.hset(id, 'current_lpu_email', current_lpu[4])
    redis_db.hset(id, 'step', 3)
    return render_to_response(template_name, {'current_lpu': current_lpu,
                                              'podrazd_list': podrazd_list,
                                              'step': int(redis_db.hget(id, 'step'))})