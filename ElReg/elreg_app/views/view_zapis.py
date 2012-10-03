#coding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from ElReg.settings import redis_db
import datetime

def index(request, template_name):
    """
    Логика страницы Запись
    """
    id = '%s' % request.session.session_key
    current_podrazd = redis_db.hget(id, 'current_podrazd')
    prof = redis_db.hget(id, 'prof')
    docName = redis_db.hget(id, 'docName')
    date = redis_db.hget(id, 'date')
    start_time = redis_db.hget(id, 'start_time')
    finish_time = redis_db.hget(id, 'finish_time')
    ticketUid = redis_db.hget(id, 'ticketUid')

    redis_db.hset(id, 'step', 8)
    return render_to_response(template_name, {
                                              'current_podrazd': current_podrazd,
                                              'prof': prof,
                                              'docName': docName,
                                              'date': date,
                                              'start_time': start_time,
                                              'finish_time': finish_time,
                                              'ticketUid': ticketUid,
                                              'step': int(redis_db.hget(id, 'step'))})
