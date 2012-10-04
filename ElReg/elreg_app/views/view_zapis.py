#coding: utf-8

from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from ElReg.settings import redis_db, client

def index(request, template_name):
    """
    Логика страницы Запись
    """
    id = '%s' % request.session.session_key

    # отправка письма:
    if request.method == 'POST':
        email = redis_db.hget(id, 'current_lpu_email')
        send_mail('>>>test: Subject<<<', '>>>test: Here is the MESSAGE!<<<', email,
        ['test@example.com'], fail_silently=False)
        return HttpResponseRedirect('/')

    hospital_Uid = redis_db.hget(id, 'hospital_Uid')
    ticket_Uid = redis_db.hget(id, 'ticketUid')

    try:
        ticketStatus = client("schedule").service.getTicketStatus(hospitalUid=hospital_Uid, ticketUid=ticket_Uid)[0]
    except:
        ticketStatus = []

    prof = redis_db.hget(id, 'prof')
    date = redis_db.hget(id, 'date')
    start_time = redis_db.hget(id, 'start_time')
    finish_time = redis_db.hget(id, 'finish_time')

    redis_db.hset(id, 'step', 8)
    return render_to_response(template_name, {'ticketStatus': ticketStatus,
                                              'prof': prof,
                                              'date': date,
                                              'start_time': start_time,
                                              'finish_time': finish_time,
                                              'current_lpu_title': redis_db.hget(id, 'current_lpu_title'),
                                              'step': int(redis_db.hget(id, 'step'))})
