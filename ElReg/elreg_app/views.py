#coding: utf-8

from django.contrib.sessions.backends.db import SessionStore
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from elreg_app.functions import *
from elreg_app.models import Region
from settings import redis_db
import datetime
import json


def moPage(request, template_name):
    """ Логика страницы МО
    Главная страница сайта. На ней происходит проверка на наличие у пользователя идентификатора сессии
    и создание сессии пользователя в случае отсутствия идентификатора. А также происходит получение
    списка доступных регионов, установленных в административном интерфейсе.

    """
#    id = request.session.session_key
#    if not id:
#        s = SessionStore()
#        s.save()
#        id = s.session_key
#    redis_db.hset(id, 'step', 1)

    r = RedisDB(request)
    r.set('step', 1)

    # получение списка регионов:
    region_list = Region.objects.filter(activation=True)
    return render_to_response(template_name, {'region_list': region_list,
                                              'step': r.get('step')})


def lpuPage(request, template_name, okato=0):
    """ Логика страницы ЛПУ
    Из полученного кода ОКАТО находим список всех ЛПУ для данного региона. Если на страницу попадаем через
    кнопку "Поиск ЛПУ", тогда  в okato передается строка search и список ЛПУ не выводится.

    """
#    id = request.session.session_key
    r = RedisDB(request)
    if not okato:
#        okato = redis_db.hget(id, 'okato')
        okato = r.get('okato')
    if okato != "search":
#        redis_db.hset(id, 'okato', okato)
        r.set('okato', okato)
        hospitals_list = ListWSDL().listHospitals(okato)
        current_region = Region.objects.get(code=okato)
#    redis_db.hset(id, 'step', 2)
    r.set('step', 2)
    step = 2
    return render_to_response(template_name, locals())


def podrazdeleniePage(request, template_name, podrazd=0):
    """Логика страницы Подразделение/Специализация/Врач
    Выводится список подразделений для выбранного ЛПУ. Остальная логика страницы осуществляется средствами jQuery с
    использованием AJAX'а и определена в представлении view_updates.py и скрипте updates.js.

    """
    id = request.session.session_key
    if not podrazd:
        podrazd = redis_db.hget(id, 'podrazd')
    info_list = InfoWSDL().getHospitalInfo()
    podrazdelenie_list = []
    current_lpu = ''
    try:
        for info in info_list:
            if info.uid.startswith(podrazd):
                current_lpu = info
                for b in info.buildings:
                    podrazdelenie_list.append(b.title)
    except AttributeError:
        return Http404

    tmp_list = []
    list_list = ListWSDL().listHospitals()
    for list in list_list:
        for w in podrazdelenie_list:
            if list.uid.startswith(podrazd) and list.title == w:
                tmp_list.append(list.uid.split('/')[1])
    podrazd_list = zip(podrazdelenie_list, tmp_list)
    redis_db.hset(id, 'podrazd', podrazd)
    redis_db.hset(id, 'current_lpu_title', current_lpu[1])
    redis_db.hset(id, 'current_lpu_email', current_lpu[4])
    redis_db.hset(id, 'step', 3)
    return render_to_response(template_name, {'current_lpu': current_lpu,
                                              'podrazd_list': podrazd_list,
                                              'step': int(redis_db.hget(id, 'step'))})


def vremyaPage(request, template_name, vremya=0):
    """Логика страницы Время
    Логика страницы Время

    """
    id = request.session.session_key
    if not vremya or vremya in ['next','prev']:
        if not vremya:
            now = datetime.date.today()
            firstweekday = now - datetime.timedelta(days=datetime.date.isoweekday(now)-1)
        elif vremya == 'next':
            a = redis_db.hget(id, 'firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) + datetime.timedelta(days=7)
        elif vremya == 'prev':
            a = redis_db.hget(id, 'firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) - datetime.timedelta(days=7)
        vremya = redis_db.hget(id, 'vremya')
    else:
        now = datetime.date.today()
        firstweekday = now - datetime.timedelta(days=datetime.date.isoweekday(now)-1)
    hospital_Uid = redis_db.hget(id, 'hospital_Uid')
    ticketList = ScheduleWSDL().getScheduleInfo(hospitalUid=hospital_Uid, doctorUid=vremya)

    docName = '' # ФИО врача
    for i in ListWSDL().listDoctors():
        if i.uid == vremya:
            docName = i.name
            docName = ' '.join([docName.lastName, docName.firstName, docName.patronymic])
            redis_db.hset(id, 'docName', docName)

    times = [] # Список времен начала записи текущей недели
    dates = [] # Список дат текущей недели

    for i in xrange(7):
        newDay = firstweekday + datetime.timedelta(days=i)
        dates.append(newDay)
        for ticket in ticketList:
            if newDay == ticket.start.date():
                times.append(ticket.start.time())
        times = list(set(times))
        times.sort()

    ticketTable = []
    if times:
        currentTicketList = []
        for ticket in ticketList:
            if ticket.start.date() in dates:
                currentTicketList.append(ticket)
        for time in times:
            tmpList = [0]*7
            for ticket in currentTicketList:
                if ticket.start.time() == time:
                    tmpList[dates.index(ticket.start.date())] = ticket
            ticketTable.append(tmpList)

    redis_db.hset(id, 'vremya', vremya)
    redis_db.hset(id, 'firstweekday', firstweekday)
    redis_db.hset(id, 'step', 4)
    return render_to_response(template_name, {'current_podrazd': redis_db.hget(id, 'current_podrazd'),
                                              'prof': redis_db.hget(id, 'prof'),
                                              'docName': docName,
                                              'dates': dates,
                                              'times': times,
                                              'ticketTable': ticketTable,
                                              'now': datetime.datetime.now(),
                                              'step': int(redis_db.hget(id, 'step'))})


def pacientPage(request, template_name):
    """Логика страницы Пациент
    Здесь происходит обработка данных полученных от пользователя (на стороне сервера). Осуществляется проверка на
    наличие незаполненных полей и упрощенная валидация введенных данных. Все найденные ошибки заносятся в
    словарь errors, который выводится в шаблон в случае присутствия в нем элементов. В случае отсутствия ошибок в
    форме с данными пользователя формируется запрос на запись в ЛПУ (ticketPatient). При отклонении записи на приём,
    причина отклонения содержится в переменной result, которая и передается в шаблон. При успешной записи на приём,
    в случае если пользователь указал e-mail (userEmail), формируется тело письма и выполняется его отправка. Далее
    осуществляется редирект на страницу Запись. При попытке попасть на страницу Пациент по средсвам введения
    url-адреса в адресную строку, будет осуществлен редирект на главную страницу.

    """
    id = request.session.session_key
    errors = []
    if request.method == 'POST':
        ticket = request.POST['ticket']
        tmp_list = ticket.split('-')
        b = tmp_list[0].split(':')
        date = datetime.date(int(b[2]), int(b[1]), int(b[0])) # Дата выбранного приема
        b = tmp_list[1].split(':')
        start_time = datetime.time(int(b[0]), int(b[1]), int(b[2])) # Время начала выбранного приема
        b = tmp_list[2].split(':')
        finish_time = datetime.time(int(b[0]), int(b[1]), int(b[2])) # Время окончания выбранного приема
        if request.POST.get('flag', ''):
            # Проверка на заполненность формы пользователем и ее корректность:
            # фамилия
            lastName = request.POST.get('lastName', '')
            if not lastName:
                errors.append(u"Введите фамилию")
            elif not stringValidation(lastName):
                errors.append(u'Введите корректно фамилию')
                # имя
            firstName = request.POST.get('firstName', '')
            if not firstName:
                errors.append(u"Введите имя")
            elif not stringValidation(firstName):
                errors.append(u'Введите корректно имя')
                # отчество
            patronymic = request.POST.get('patronymic', '')
            if not patronymic:
                errors.append(u"Введите отчество")
            elif not stringValidation(patronymic):
                errors.append(u'Введите корректно отчество')
                # день рождения
            dd = request.POST.get('dd', '')
            mm = request.POST.get('mm', '')
            yy = request.POST.get('yy', '')
            if not dd or not mm or not yy:
                errors.append(u'Введите дату рождения')
                # полис
            policy1 = request.POST.get('policy1', '')
            policy2 = request.POST.get('policy2', '')
            if not policy2:
                errors.append(u"Введите серию и номер полиса")
                # электронная почта
            userEmail = request.POST.get('email', '')
            if userEmail and not emailValidation(userEmail):
                errors.append(u'Введите корректно адрес электронной почты')

            ticketPatient_err = ''
            prof = redis_db.hget(id, 'prof')
            # если ошибок в форме нет
            if not errors:
                hospital_Uid = redis_db.hget(id, 'hospital_Uid')
                vremya = redis_db.hget(id, 'vremya')
                omiPolicyNumber = ' '.join([policy1,policy2])
                pacientName = ' '.join([lastName,firstName,patronymic])
                ticketPatient = ScheduleWSDL().enqueue(
                    person = {'lastName': unicode(lastName),
                              'firstName': unicode(firstName),
                              'patronymic': unicode(patronymic)},
                    omiPolicyNumber = unicode(omiPolicyNumber),
                    hospitalUid = hospital_Uid,
                    doctorUid = vremya,
                    timeslotStart = str(date) + 'T' + str(start_time),
                    hospitalUidFrom = unicode("0"),
                    birthday = unicode('-'.join([yy,mm,dd]))
                )
                # запись на приём произошла успешно:
                if not ticketPatient['result']:
                    redis_db.hset(id, 'ticketUid', ticketPatient['ticketUid'])
                    redis_db.hset(id, 'date', date)
                    redis_db.hset(id, 'start_time', start_time)
                    redis_db.hset(id, 'finish_time', finish_time)
                    redis_db.hset(id, 'finish_time', finish_time)
                    redis_db.hset(id, 'omiPolicyNumber', omiPolicyNumber)
                    redis_db.hset(id, 'pacientName', pacientName)
                    redis_db.hset(id, 'birthday', '.'.join([dd,mm,yy]))
                    # формирование и отправка письма:
                    if userEmail:
                        emailLPU = redis_db.hget(id, 'current_lpu_email')
                        plaintext = get_template('email.txt')
                        htmly     = get_template('email.html')

                        context = Context({ 'ticketUid': ticketPatient['ticketUid'],
                                            'pacientName': redis_db.hget(id, 'pacientName'),
                                            'birthday': redis_db.hget(id, 'birthday'),
                                            'omiPolicyNumber': redis_db.hget(id, 'omiPolicyNumber'),
                                            'current_podrazd': redis_db.hget(id, 'current_podrazd'),
                                            'docName': redis_db.hget(id, 'docName'),
                                            'prof': redis_db.hget(id, 'prof'),
                                            'date': date,
                                            'start_time': start_time,
                                            'finish_time': finish_time })

                        subject, from_email, to = u'Уведомление о записи на приём', emailLPU, userEmail
                        text_content = plaintext.render(context)
                        html_content = htmly.render(context)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    return HttpResponseRedirect(reverse('zapis'))
                # ошибка записи на приём:
                else:
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
        return HttpResponseRedirect(reverse('mo'))


def zapisPage(request, template_name):
    """Логика страницы Запись
    Запись на приём прошла успешно. Здесь происходит запрос на получение сведений о записи (номер талона, имя врача,
    название ЛПУ и т.д.). Далее эти данные передаются в шаблон для вывода на экран и на печать, при необходимости.

    """
    id = request.session.session_key
    hospital_Uid = redis_db.hget(id, 'hospital_Uid')
    ticket_Uid = redis_db.hget(id, 'ticketUid')

    ticketStatus = ScheduleWSDL().getTicketStatus(hospitalUid=hospital_Uid, ticketUid=ticket_Uid)

    prof = redis_db.hget(id, 'prof')
    date = redis_db.hget(id, 'date')
    d = date.split('-')
    dd = datetime.date(int(d[0]),int(d[1]),int(d[2]))
    start_time = redis_db.hget(id, 'start_time')
    finish_time = redis_db.hget(id, 'finish_time')
    omiPolicyNumber = redis_db.hget(id, 'omiPolicyNumber')
    pacientName = redis_db.hget(id, 'pacientName')
    birthday = redis_db.hget(id, 'birthday')

    redis_db.hset(id, 'step', 6)
    return render_to_response(template_name, {'ticketStatus': ticketStatus,
                                              'prof': prof,
                                              'date': dd,
                                              'start_time': start_time,
                                              'finish_time': finish_time,
                                              'omiPolicyNumber': omiPolicyNumber,
                                              'pacientName': pacientName,
                                              'birthday': birthday,
                                              'current_lpu_title': redis_db.hget(id, 'current_lpu_title'),
                                              'step': int(redis_db.hget(id, 'step'))})


##### Представления, используемые AJAX'ом: #####

def updatesPage(request):
    """ Логика страницы updates
    Представление создано только для динамической подгрузки данных при помощи AJAX'а. Вызывается на вкладке
    "Подразделение/Специализация/Врач". Возвращает ответ в формате JSON. Запуск через адресную строку приведет к редиректу на главную страницу.

    """
    id = request.session.session_key
    doctors_list = ListWSDL().listDoctors()
    tmp, new = [], {}

    # при щелчке на элементе из таблицы со списком подразделений:
    if 'clickSpec' in request.GET:
        spec = request.GET['clickSpec']
        redis_db.hset(id, 'spec', spec)
        for i in doctors_list:
            if i.hospitalUid == '/'.join([redis_db.hget(id, 'podrazd'), spec]):
                tmp.append(i.speciality)
                tmp = list(set(tmp))
        new = dict(zip(xrange(len(tmp)), tmp))

    # при щелчке на элементе из таблицы со списком специализаций:
    elif 'clickProf' in request.GET:
        prof = request.GET['clickProf']
        hospital_Uid = '/'.join([redis_db.hget(id, 'podrazd'), redis_db.hget(id, 'spec')])
        for i in doctors_list:
            if i.hospitalUid == hospital_Uid and i.speciality == prof:
                tmp.append(i)
        for i in tmp:
            new[i.uid] = ' '.join([i.name.lastName, i.name.firstName, i.name.patronymic])

    # при обращении к странице через адресную строку:
    else:
        return HttpResponseRedirect(reverse('mo'))

    # создание ответа в формате json:
    return HttpResponse(json.dumps(new), mimetype='application/json')


def searchPage(request):
    """ Логика страницы search
    Представление создано только для динамической подгрузки данных при помощи AJAX'а. Вызывается на вкладке "ЛПУ".
    Предназначена для поиска ЛПУ по его названию или части названия, по названию или части названия города в котором
    оно находится, по названию или части названия района в котором оно находится. Возвращает ответ в формате JSON.
    Запуск через адресную строку приведет к редиректу на главную страницу.

    """
    if request.method == 'GET':
        search_lpu = request.GET.get('search_lpu', '')
        search_gorod = request.GET.get('search_gorod', '')
        search_rayon = request.GET.get('search_rayon', '')
        # если содержимое полей поиска не пустое:
        if search_lpu or search_gorod or search_rayon:
            result = {}

            ### поиск ЛПУ по названию: ###
            if search_lpu:
                tmp_list = []
                # получение списка введенных пользователем слов
                search_list = search_lpu.lower().split(' ')

                # формирование временного списка кортежей [(uid ЛПУ, наименование ЛПУ), ...]
                for i in InfoWSDL().getHospitalInfo():
                    tmp_list.append((i.uid.split('/')[0], i.title.lower()))
                # формирование словаря со значениями, удовлетворяющими поиску,
                # где ключ - uid ЛПУ, а значение - наименование ЛПУ
                for (uid,title) in tmp_list:
                    flag = True
                    for i in search_list:
                        if title.find(i) == -1:
                            flag = False
                    if flag:
                        result[uid] = title

            ### поиск ЛПУ по названию города: ###
            if search_gorod:
                tmp_list = []
                tmp_dict ={}
                lpu_dict = {}
                # формирование списка доступных городов:
                region_list = Region.objects.filter(activation=True).exclude(region__iendswith=u'район')

                # получение списка введенных пользователем слов
                search_list = search_gorod.lower().split(' ')

                # формирование временного списка кортежей [(регион, код ОКАТО), ...]
                for i in region_list:
                    tmp_list.append((i.region.lower(), i.code))

                # формирование словаря со значениями, удовлетворяющими поиску,
                # где ключ - uid ЛПУ, а значение - наименование ЛПУ
                for (region,code) in tmp_list:
                    flag = True
                    for i in search_list:
                        if region.find(i) == -1:
                            flag = False
                    if flag:
                        tmp_dict[code] = region
                for i in tmp_dict.keys():
                    hospitals_list = ListWSDL().listHospitals(i)
                    for j in hospitals_list:
                        lpu_dict[j.uid.split('/')[0]] = j.title

                if not result:
                    result = lpu_dict

                else:
                    adict = {}
                    for i in result.items():
                        for j in lpu_dict.keys():
                            if i[0] == j:
                                adict[i[0]] = i[1]
                    result = adict

            ### поиск ЛПУ по названию района: ###
            if search_rayon:
                tmp_list = []
                lpu_dict = {}
                # формирование списка доступных районов:
                region_list = Region.objects.filter(activation=True, region__iendswith=u'район')

                # получение списка введенных пользователем слов
                search_list = search_rayon.lower().split(' ')

                # формирование временного списка кортежей [(регион, код ОКАТО), ...]
                for i in region_list:
                    tmp_list.append((i.region.lower(), i.code))

                # формирование словаря со значениями, удовлетворяющими поиску,
                # где ключ - uid ЛПУ, а значение - наименование ЛПУ
                tmp_dict ={}
                for (region,code) in tmp_list:
                    flag = True
                    for i in search_list:
                        if region.find(i) == -1:
                            flag = False
                    if flag:
                        tmp_dict[code] = region
                for i in tmp_dict.keys():
                    hospitals_list = ListWSDL().listHospitals(i)
                    for j in hospitals_list:
                        lpu_dict[j.uid.split('/')[0]] = j.title
                if not result:
                    result = lpu_dict
                else:
                    adict = {}
                    for i in result.items():
                        for j in lpu_dict.keys():
                            if i[0] == j:
                                adict[i[0]] = i[1]
                    result = adict

            # создание ответа в формате json из содержимого словаря result:
            return HttpResponse(json.dumps(result), mimetype='application/json')

    # при обращении к странице через адресную строку:
    else:
        return HttpResponseRedirect(reverse('mo'))
