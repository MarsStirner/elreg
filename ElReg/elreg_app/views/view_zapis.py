#coding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from ElReg.settings import redis_db
import datetime

def index(request, template_name):
    """
    Логика страницы Запись
    """





# if request.method == 'POST':
#        ticket = request.POST['ticket']
#        tmp_lst = ticket.split('-')
#        b = tmp_lst[0].split(':')
#        date = datetime.date(int(b[2]), int(b[1]), int(b[0])) # Дата выбранного приема
#        b = tmp_lst[1].split(':')
#        start_time = datetime.time(int(b[0]), int(b[1]), int(b[2])) # Время начала выбранного приема
#        b = tmp_lst[2].split(':')
#        finish_time = datetime.time(int(b[0]), int(b[1]), int(b[2])) # Время окончания выбранного приема
#        start_date = datetime.datetime.combine(date, start_time) # Дата и время начала выбранного приема
#        finish_date = datetime.datetime.combine(date, finish_time) # Дата и время окончания выбранного приема
#
#    else:
#        return HttpResponseRedirect("/")
#
#    current_podrazd = redis_db.get('current_podrazd')
#    prof = redis_db.get('prof')
#    docName = [redis_db.get('docLastName'), redis_db.get('docFirstName'), redis_db.get('docPatronymic')]

    redis_db.set('step', 8)
    return render_to_response(template_name, {
#                                              'current_podrazd': current_podrazd,
#                                              'prof': prof,
#                                              'docName': docName,
#                                              'date': date,
#                                              'start_time': start_time,
#                                              'finish_time': finish_time,
                                              'step': int(redis_db.get('step'))})
