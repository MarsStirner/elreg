#coding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from ElReg.settings import redis_db
from elreg_app.functions import ScheduleWSDL

def index(request, template_name):
    """Логика страницы Запись
    Логика страницы Запись
    """
    id = request.session.session_key
    hospital_Uid = redis_db.hget(id, 'hospital_Uid')
    ticket_Uid = redis_db.hget(id, 'ticketUid')

    ticketStatus = ScheduleWSDL().getTicketStatus(hospitalUid=hospital_Uid, ticketUid=ticket_Uid)

    prof = redis_db.hget(id, 'prof')
    date = redis_db.hget(id, 'date')
    start_time = redis_db.hget(id, 'start_time')
    finish_time = redis_db.hget(id, 'finish_time')
    omiPolicyNumber = redis_db.hget(id, 'omiPolicyNumber')
    pacientName = redis_db.hget(id, 'pacientName')
    birthday = redis_db.hget(id, 'birthday')

    redis_db.hset(id, 'step', 6)
    return render_to_response(template_name, {'ticketStatus': ticketStatus,
                                              'prof': prof,
                                              'date': date,
                                              'start_time': start_time,
                                              'finish_time': finish_time,
                                              'omiPolicyNumber': omiPolicyNumber,
                                              'pacientName': pacientName,
                                              'birthday': birthday,
                                              'current_lpu_title': redis_db.hget(id, 'current_lpu_title'),
                                              'step': int(redis_db.hget(id, 'step'))})
