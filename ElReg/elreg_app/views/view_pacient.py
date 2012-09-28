#coding: utf-8

from django.shortcuts import render_to_response
from ElReg.settings import redis_db, client_list, client_schedule
import datetime

def index(request, template_name, pacient='0'):
    """
    Логика страницы Пациент
    """
    try:
        hospital_Uid = redis_db.get('hospital_Uid')
        ticketList = client_schedule.service.getScheduleInfo(hospitalUid=hospital_Uid, doctorUid=vremya)
    except:
        ticketList = []

    current_podrazd = redis_db.get('current_podrazd')
    prof = redis_db.get('prof')
    docName = [redis_db.get('docLastName'), redis_db.get('docFirstName'), redis_db.get('docPatronymic')]

    redis_db.set('step', 7)
    return render_to_response(template_name, {'current_podrazd': current_podrazd,
                                              'prof': prof,
                                              'docName': docName,
                                              'step': redis_db.get('step')})
