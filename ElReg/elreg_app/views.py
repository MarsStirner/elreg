# -*- coding: utf-8 -*-

from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from elreg_app.functions import *
from elreg_app.models import Region
import datetime
import json


def moPage(request, template_name):
    """ Логика страницы МО
    Главная страница сайта. На ней происходит проверка на наличие у пользователя идентификатора сессии
    и создание сессии пользователя в случае отсутствия идентификатора. А также происходит получение
    списка доступных регионов, установленных в административном интерфейсе.

    """
    db = Redis(request)
    # получение списка регионов:
    region_list = Region.objects.filter(activation=True)
    db.set('step', 1)
    return render_to_response(template_name, {'region_list': region_list,
                                              'step': db.get('step')})


def lpuPage(request, template_name, okato=0):
    """ Логика страницы ЛПУ
    Из полученного кода ОКАТО находим список всех ЛПУ для данного региона. Если на страницу попадаем через
    кнопку "Поиск ЛПУ", тогда  в okato передается строка search и список ЛПУ не выводится.

    """
    db = Redis(request)
    if not okato:
        okato = db.get('okato')
    if okato != "search":
        db.set('okato', okato)
        hospitals_list = ListWSDL().listHospitals(okato)
        current_region = Region.objects.get(code=okato)
    db.set('step', 2)
    step = 2
    return render_to_response(template_name, locals())


def podrazdeleniePage(request, template_name, podrazd=0):
    """Логика страницы Подразделение/Специализация/Врач
    Выводится список подразделений для выбранного ЛПУ. Остальная логика страницы осуществляется средствами jQuery с
    использованием AJAX'а и определена в скрипте updates.js.

    """
    db = Redis(request)
    if not podrazd:
        podrazd = db.get('podrazd')
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
                tmp_list.append((list.uid.split('/')[1], list.address))
    podrazd_list = zip(podrazdelenie_list, tmp_list)
    db.sets({'podrazd': podrazd,
            'current_lpu_title': current_lpu[1],
            'current_lpu_phone': current_lpu[3],
            'current_lpu_email': current_lpu[4],
            'step': 3
            })
    return render_to_response(template_name, {'current_lpu': current_lpu,
                                              'podrazd_list': podrazd_list,
                                              'step': db.get('step')})


def vremyaPage(request, template_name, vremya=0):
    """Логика страницы Время
    Выводится таблица с расписанием выбранного врача на текущую неделю.

    """
    db = Redis(request)
    now = datetime.date.today()
    # если попадаем на страницу нажимая кнопку "Назад", "Предыдущая" или "Следующая":
    if not vremya or vremya in ['next','prev']:
        if not vremya:
            firstweekday = now - datetime.timedelta(days=datetime.date.isoweekday(now)-1)
        elif vremya == 'next':
            a = db.get('firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) + datetime.timedelta(days=7)
        elif vremya == 'prev':
            a = db.get('firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) - datetime.timedelta(days=7)
        vremya = db.get('vremya').split('-')
    # если попадаем на страницу после выбора врача на вкладке "Подраздеелние/Специализация/Врач":
    else:
        firstweekday = now - datetime.timedelta(days=datetime.date.isoweekday(now)-1)
    hospital_Uid = db.get('hospital_Uid')
    ticketList = ScheduleWSDL().getScheduleInfo(hospitalUid=hospital_Uid, doctorUid=vremya)

    docName = '' # ФИО врача
    for i in ListWSDL().listDoctors():
        if i.uid == vremya:
            docName = i.name
            docName = ' '.join([docName.lastName, docName.firstName, docName.patronymic])
            db.set('docName', docName)

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

    db.sets({'vremya': vremya,
            'firstweekday': firstweekday,
            'step': 4
            })
    return render_to_response(template_name, {
                                              'current_lpu_title': db.get('current_lpu_title'),
                                              'current_lpu_phone': db.get('current_lpu_phone'),
                                              'adress': db.get('adress'),
                                              'prof': db.get('prof'),
                                              'docName': docName,
                                              'dates': dates,
                                              'times': times,
                                              'ticketTable': ticketTable,
                                              'now': datetime.datetime.now(),
                                              'step': db.get('step')})


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
    db = Redis(request)
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
        # если представление было вызвано при нажатии кнопки submit на странице Пациент:
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
            # если ошибок в форме нет
            if not errors:
                hospital_Uid = db.get('hospital_Uid')
                vremya = db.get('vremya')
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
                if ticketPatient['result'] == 'true':
                    db.sets({'ticketUid': ticketPatient['ticketUid'],
                             'date': date,
                             'start_time': start_time,
                             'finish_time': finish_time,
                             'omiPolicyNumber': omiPolicyNumber,
                             'pacientName': pacientName,
                             'birthday': '.'.join([dd,mm,yy])
                            })
                    # формирование и отправка письма:
                    if userEmail:
                        emailLPU = db.get('current_lpu_email')
                        plaintext = get_template('email.txt')
                        htmly     = get_template('email.html')

                        context = Context({ 'ticketUid': ticketPatient['ticketUid'],
                                            'pacientName': db.get('pacientName'),
                                            'birthday': db.get('birthday'),
                                            'omiPolicyNumber': db.get('omiPolicyNumber'),
                                            'current_podrazd': db.get('current_podrazd'),
                                            'current_lpu_title': db.get('current_lpu_title'),
                                            'docName': db.get('docName'),
                                            'prof': db.get('prof'),
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
            # ошибка при записи на приём или ошибки в заполненной форме:
            db.set('step', 5)
            return render_to_response(template_name, {
                                                      'current_podrazd': db.get('current_podrazd'),
                                                      'current_lpu_title': db.get('current_lpu_title'),
                                                      'prof': db.get('prof'),
                                                      'docName': db.get('docName'),
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
                                                      'step': db.get('step')})
        # если представление было вызвано нажатием на ячейку таблицы на странице Время:
        db.set('step', 5)
        return render_to_response(template_name, {
                                                  'current_lpu_title': db.get('current_lpu_title'),
                                                  'current_lpu_phone': db.get('current_lpu_phone'),
                                                  'adress': db.get('adress'),
                                                  'prof': db.get('prof'),
                                                  'docName': db.get('docName'),
                                                  'errors': errors,
                                                  'ticket': ticket,
                                                  'date': date,
                                                  'start_time': start_time,
                                                  'finish_time': finish_time,
                                                  'step': db.get('step')})
    # обращение к форме через адресную строку:
    else:
        return HttpResponseRedirect(reverse('mo'))


def zapisPage(request, template_name):
    """Логика страницы Запись
    Запись на приём прошла успешно. Здесь происходит запрос на получение сведений о записи (номер талона, имя врача,
    название ЛПУ и т.д.). Далее эти данные передаются в шаблон для вывода на экран и на печать, при необходимости.

    """
    db = Redis(request)
    ticketUid = db.get('ticketUid')


    prof = db.get('prof')
    date = db.get('date')
    d = date.split('-')
    dd = datetime.date(int(d[0]),int(d[1]),int(d[2]))
    start_time = db.get('start_time')
    finish_time = db.get('finish_time')
    omiPolicyNumber = db.get('omiPolicyNumber')
    pacientName = db.get('pacientName')
    birthday = db.get('birthday')
    docName = db.get('docName')

    db.set('step', 6)
    return render_to_response(template_name, {'ticketUid': ticketUid,
                                              'prof': prof,
                                              'date': dd,
                                              'start_time': start_time,
                                              'finish_time': finish_time,
                                              'omiPolicyNumber': omiPolicyNumber,
                                              'pacientName': pacientName,
                                              'birthday': birthday,
                                              'docName': docName,
                                              'current_podrazd': db.get('current_podrazd'),
                                              'current_lpu_title': db.get('current_lpu_title'),
                                              'step': db.get('step')})


##### Представления, используемые AJAX'ом: #####

def updatesPage(request):
    """ Логика страницы updates
    Представление создано только для динамической подгрузки данных при помощи AJAX'а. Вызывается на вкладке
    "Подразделение/Специализация/Врач". Возвращает ответ в формате JSON. Запуск через адресную строку приведет к
    редиректу на главную страницу.

    """
    db = Redis(request)
    doctors_list = ListWSDL().listDoctors()
    tmp, new = [], {}

    # при щелчке на элементе из таблицы со списком подразделений:
    if 'clickSpec' in request.GET:
        spec = request.GET['clickSpec']
        adress = request.GET['value']
        db.sets({'adress': adress,
                 'spec': spec
                })
        for i in doctors_list:
            if i.hospitalUid == '/'.join([db.get('podrazd'), spec]):
                tmp.append(i.speciality)
                tmp = list(set(tmp))
                tmp.sort()
        new = dict(zip(xrange(len(tmp)), tmp))
        hospitals_list = ListWSDL().listHospitals()
        for i in hospitals_list:
            if i.uid.startswith('/'.join([db.get('podrazd'), spec])):
                db.set('current_podrazd', i.title)

    # при щелчке на элементе из таблицы со списком специализаций:
    elif 'clickProf' in request.GET:
        prof = request.GET['clickProf']
        hospital_Uid = '/'.join([db.get('podrazd'), db.get('spec')])
        db.sets({'prof': prof,
                 'hospital_Uid': hospital_Uid
                })
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
