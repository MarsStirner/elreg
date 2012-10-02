#coding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from ElReg.settings import redis_db
import datetime

def index(request, template_name):
    """
    Логика страницы Запись
    """

    current_podrazd = redis_db.get('current_podrazd')
    prof = redis_db.get('prof')
    docName = redis_db.get('docName')
    date = redis_db.get('date')
    start_time = redis_db.get('start_time')
    finish_time = redis_db.get('finish_time')

    redis_db.set('step', 8)
    return render_to_response(template_name, {
                                              'current_podrazd': current_podrazd,
                                              'prof': prof,
                                              'docName': docName,
                                              'date': date,
                                              'start_time': start_time,
                                              'finish_time': finish_time,
                                              'step': int(redis_db.get('step'))})
