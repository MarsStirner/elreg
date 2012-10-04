#coding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from ElReg.settings import redis_db, client
from elreg_app.functions import *
import datetime

def index(request, template_name):
    """
    Логика страницы Пациент
    """
    id = '%s' % request.session.session_key
    errors = []
    if request.method == 'POST':
        ticket = request.POST['ticket']

        # !!! есть ошибка: если ticket_err возвращает str, то переменная ticket содержит бред
        tmp_lst = ticket.split('-')
        b = tmp_lst[0].split(':')
        date = datetime.date(int(b[2]), int(b[1]), int(b[0])) # Дата выбранного приема
        b = tmp_lst[1].split(':')
        start_time = datetime.time(int(b[0]), int(b[1]), int(b[2])) # Время начала выбранного приема
        b = tmp_lst[2].split(':')
        finish_time = datetime.time(int(b[0]), int(b[1]), int(b[2])) # Время окончания выбранного приема
        start_date = datetime.datetime.combine(date, start_time) # Дата и время начала выбранного приема
        finish_date = datetime.datetime.combine(date, finish_time) # Дата и время окончания выбранного приема
        if request.POST.get('flag', ''):
            # Проверка на заполненность формы пользователем и ее корректность
            lastName = request.POST.get('lastName', '')
            if not lastName:
                errors.append(u"Введите фамилию")
            else:
                if not stringcorrect(lastName):
                    errors.append(u'Введите корректно фамилию')

            firstName = request.POST.get('firstName', '')
            if not firstName:
                errors.append(u"Введите имя")
            else:
                if not stringcorrect(firstName):
                    errors.append(u'Введите корректно имя')

            patronymic = request.POST.get('patronymic', '')
            if not patronymic:
                errors.append(u"Введите отчество")
            else:
                if not stringcorrect(patronymic):
                    errors.append(u'Введите корректно отчество')

            dd = request.POST.get('dd', '')
            mm = request.POST.get('mm', '')
            yy = request.POST.get('yy', '')
            if not dd or not mm or not yy:
                errors.append(u'Введите дату рождения')

            policy1 = request.POST.get('policy1', '')
            policy2 = request.POST.get('policy2', '')
            if not policy2:
                errors.append(u"Введите серию и номер полиса")

            email = request.POST.get('email', '')
            if not email:
                errors.append(u"Введите e-mail")

            ticket_err = ''
            prof = redis_db.hget(id, 'prof')
            # если ошибок в форме нет
            if not errors:
                hospital_Uid = redis_db.hget(id, 'hospital_Uid')
                vremya = redis_db.hget(id, 'vremya')
                omiPolicyNumber = "%s %s"%(policy1,policy2)

                ticket = client("schedule").service.enqueue(
                    person = {
                        'lastName': unicode(lastName),
                        'firstName': unicode(firstName),
                        'patronymic': unicode(patronymic) },
                    omiPolicyNumber = unicode(omiPolicyNumber),
                    hospitalUid = hospital_Uid,
#                    speciality = unicode(prof),
                    doctorUid = vremya,
                    timeslotStart = str(date) + 'T' + str(start_time),
                    hospitalUidFrom = unicode("0"),
                    birthday = unicode("%s-%s-%sT0"%(yy,mm,dd)),
                )

                if not ticket['result']: # запись прошла усешно
                    redis_db.hset(id, 'ticketUid', ticket['ticketUid'])
                    redis_db.hset(id, 'date', date)
                    redis_db.hset(id, 'start_time', start_time)
                    redis_db.hset(id, 'finish_time', finish_time)
                    return HttpResponseRedirect('/zapis')
                else: # ошибка записи
                    ticket_err = ticket['result']


            current_podrazd = redis_db.hget(id, 'current_podrazd')
            docName = redis_db.hget(id, 'docName')

            redis_db.hset(id, 'step', 7)
            return render_to_response(template_name, {'current_podrazd': current_podrazd,
                                                      'prof': prof,
                                                      'docName': docName,
                                                      'errors': errors,
                                                      'ticket': ticket,
                                                      'date': date,
                                                      'start_time': start_time,
                                                      'finish_time': finish_time,
                                                      'lastName': lastName,
                                                      'firstName': firstName,
                                                      'patronymic': patronymic,
                                                      'dd': dd,
                                                      'mm': mm,
                                                      'yy': yy,
                                                      'policy1': policy1,
                                                      'policy2': policy2,
                                                      'email': email,
                                                      'ticket_err': ticket_err,
                                                      'step': int(redis_db.hget(id, 'step'))})

        current_podrazd = redis_db.hget(id, 'current_podrazd')
        prof = redis_db.hget(id, 'prof')
        docName = redis_db.hget(id, 'docName')

        redis_db.hset(id, 'step', 7)
        return render_to_response(template_name, {'current_podrazd': current_podrazd,
                                                  'prof': prof,
                                                  'docName': docName,
                                                  'errors': errors,
                                                  'ticket': ticket,
                                                  'date': date,
                                                  'start_time': start_time,
                                                  'finish_time': finish_time,
                                                  'step': int(redis_db.hget(id, 'step'))})
    else:
        return HttpResponseRedirect("/")