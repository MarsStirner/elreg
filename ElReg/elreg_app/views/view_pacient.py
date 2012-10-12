#coding: utf-8

from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import Context
from ElReg.settings import redis_db
from elreg_app.functions import *
import datetime


def index(request, template_name):
    """
    Логика страницы Пациент
    """
    id = request.session.session_key
    errors = []
    if request.method == 'POST':
        ticket = request.POST['ticket']
        tmp_lst = ticket.split('-')
        b = tmp_lst[0].split(':')
        date = datetime.date(int(b[2]), int(b[1]), int(b[0])) # Дата выбранного приема
        b = tmp_lst[1].split(':')
        start_time = datetime.time(int(b[0]), int(b[1]), int(b[2])) # Время начала выбранного приема
        b = tmp_lst[2].split(':')
        finish_time = datetime.time(int(b[0]), int(b[1]), int(b[2])) # Время окончания выбранного приема
        if request.POST.get('flag', ''):
            # Проверка на заполненность формы пользователем и ее корректность
            lastName = request.POST.get('lastName', '')
            if not lastName:
                errors.append(u"Введите фамилию")
            elif not stringValidation(lastName):
                errors.append(u'Введите корректно фамилию')

            firstName = request.POST.get('firstName', '')
            if not firstName:
                errors.append(u"Введите имя")
            elif not stringValidation(firstName):
                errors.append(u'Введите корректно имя')

            patronymic = request.POST.get('patronymic', '')
            if not patronymic:
                errors.append(u"Введите отчество")
            elif not stringValidation(patronymic):
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

            userEmail = request.POST.get('email', '')
            if userEmail and not emailValidation(userEmail):
                errors.append(u'Введите корректно адрес электронной почты')

            ticketPatient_err = ''
            prof = redis_db.hget(id, 'prof')
            # если ошибок в форме нет
            if not errors:
                hospital_Uid = redis_db.hget(id, 'hospital_Uid')
                vremya = redis_db.hget(id, 'vremya')
                omiPolicyNumber = "%s %s"%(policy1,policy2)
                pacientName = "%s %s %s"%(lastName,firstName,patronymic)

                ticketPatient = ScheduleWSDL().enqueue(
                    person = {
                        'lastName': unicode(lastName),
                        'firstName': unicode(firstName),
                        'patronymic': unicode(patronymic) },
                    omiPolicyNumber = unicode(omiPolicyNumber),
                    hospitalUid = hospital_Uid,
                    doctorUid = vremya,
                    timeslotStart = str(date) + 'T' + str(start_time),
                    hospitalUidFrom = unicode("0"),
                    birthday = unicode("%s-%s-%s"%(yy,mm,dd)),
                )

                if not ticketPatient['result']: # запись прошла усешно
                    redis_db.hset(id, 'ticketUid', ticketPatient['ticketUid'])
                    redis_db.hset(id, 'date', date)
                    redis_db.hset(id, 'start_time', start_time)
                    redis_db.hset(id, 'finish_time', finish_time)
                    redis_db.hset(id, 'finish_time', finish_time)
                    redis_db.hset(id, 'omiPolicyNumber', omiPolicyNumber)
                    redis_db.hset(id, 'pacientName', pacientName)
                    redis_db.hset(id, 'birthday', "%s.%s.%s"%(dd,mm,yy))
                    # отправка письма:
                    if userEmail:
                        emailLPU = redis_db.hget(id, 'current_lpu_email')

                        plaintext = get_template('email.txt')
                        htmly     = get_template('email.html')

                        d = Context({ 'pacientName': redis_db.hget(id, 'pacientName'),
                                      'birthday': redis_db.hget(id, 'birthday'),
                                      'omiPolicyNumber': redis_db.hget(id, 'omiPolicyNumber'),
                                      'current_podrazd': redis_db.hget(id, 'current_podrazd'),
                                      'docName': redis_db.hget(id, 'docName'),
                                      'prof': redis_db.hget(id, 'prof'),
                                      'date': date,
                                      'start_time': start_time,
                                      'finish_time': finish_time })

                        subject, from_email, to = u'Уведомление о записи на приём', emailLPU, userEmail
                        text_content = plaintext.render(d)
                        html_content = htmly.render(d)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                        return HttpResponseRedirect('/zapis')






                else: # ошибка записи
                    ticketPatient_err = ticketPatient['result']


            current_podrazd = redis_db.hget(id, 'current_podrazd')
            docName = redis_db.hget(id, 'docName')

            redis_db.hset(id, 'step', 5)
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
                                                      'userEmail': userEmail,
                                                      'ticketPatient_err': ticketPatient_err,
                                                      'step': int(redis_db.hget(id, 'step'))})

        current_podrazd = redis_db.hget(id, 'current_podrazd')
        prof = redis_db.hget(id, 'prof')
        docName = redis_db.hget(id, 'docName')

        redis_db.hset(id, 'step', 5)
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