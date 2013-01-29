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
import math
import pytz
from django.utils import timezone
from livesettings import config_value
from django.core.mail import get_connection
import settings
from django import forms
from captcha.fields import CaptchaField

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

try:
    import json
except ImportError:
    import simplejson as json


def indexPage(request, templateName):
    """ Логика страницы МО
    Главная страница сайта. На ней происходит проверка на наличие у пользователя идентификатора сессии
    и создание сессии пользователя в случае отсутствия идентификатора. А также происходит получение
    списка доступных регионов, установленных в административном интерфейсе.

    """
    db = Redis(request)
    # получение списка регионов:
    region_list = Region.objects.filter(activation=True)
    db.set('step', 1)

    return render_to_response(templateName, {'region_list': region_list,
                                             'break_keys': (math.ceil(len(region_list)/3.), math.ceil(2*len(region_list)/3.),),},
                                              context_instance=RequestContext(request))


def medicalInstitutionPage(request, templateName, okato=0):
    """ Логика страницы ЛПУ
    Из полученного кода ОКАТО находим список всех ЛПУ для данного региона. Если на страницу попадаем через
    кнопку "Поиск ЛПУ", тогда  в okato передается строка search и список ЛПУ не выводится.

    """
    db = Redis(request)
    if not okato:
        okato = db.get('okato')
    if not okato:
        # в случае прямого перехода на страницу
        return HttpResponseRedirect(reverse('index'))
    if okato != "search":
        db.set('okato', okato)
        hospitals_list = ListWSDL().listHospitals(okato) # список ЛПУ выбранного региона
        current_region = Region.objects.get(code=okato) # название выбранного региона
    db.set('step', 2)
    return render_to_response(templateName, locals(),
                                             context_instance=RequestContext(request))


def subdivisionPage(request, templateName, sub=0):
    """Логика страницы Подразделение/Специализация/Врач
    Выводится список подразделений для выбранного ЛПУ. Остальная логика страницы осуществляется средствами jQuery с
    использованием AJAX'а и определена в скрипте updates.js.

    """
    db = Redis(request)
    if not sub:
        sub = db.get('sub')

    hospitalUid = 0
    try:
        hospitalUid = sub.split('/')[0]+'/0'
    except:
        pass

    tmp1_list, tmp2_list = [], []
    current_lpu = ''
    try:
        if hospitalUid:
            hospital = InfoWSDL().getHospitalInfo(hospitalUid=hospitalUid)
        else:
            hospital = InfoWSDL().getHospitalInfo()

        for i in hospital:
            if i.uid.startswith(sub):
                current_lpu = i
                for j in i.buildings:
                    tmp1_list.append(j.title)
    except AttributeError:
        raise Http404

    for i in ListWSDL().listHospitals():
        for j in tmp1_list:
            if i.uid.startswith(sub) and i.title == j:
                tmp2_list.append((i.uid.split('/')[1], i.address))
    tmp1_list.sort()
    subdivision_list = zip(tmp1_list, tmp2_list)
    db.set({'sub': sub,
            'current_lpu_title': current_lpu[1],
            'current_lpu_phone': current_lpu[3],
            'current_lpu_email': current_lpu[4],
            'step': 3})
    return render_to_response(templateName, {'current_lpu': current_lpu,
                                              'subdivision_list': subdivision_list},
                                              context_instance=RequestContext(request))


def timePage(request, templateName, time=0):
    """Логика страницы Время
    Выводится таблица с расписанием выбранного врача на текущую неделю.

    """

    try:
        timezone.activate(pytz.timezone(config_value('TZ','TIME_ZONE')))
    except:
        timezone.activate(pytz.timezone(settings.TIME_ZONE))

    db = Redis(request)
    today = datetime.date.today()
    # если попадаем на страницу нажимая кнопку "Назад", "Предыдущая" или "Следующая":
    if not time or time in ['next','prev']:
        if not time:
            firstweekday = today - datetime.timedelta(days=datetime.date.isoweekday(today)-1)
        elif time == 'next':
            a = db.get('firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) + datetime.timedelta(days=7)
        elif time == 'prev':
            a = db.get('firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) - datetime.timedelta(days=7)
        time = db.get('time')
    # если попадаем на страницу после выбора врача на вкладке "Подраздеелние/Специализация/Врач":
    else:
        firstweekday = today - datetime.timedelta(days=datetime.date.isoweekday(today)-1)
    hospital_Uid = db.get('hospital_Uid')
    ticketList = ScheduleWSDL().getScheduleInfo(hospitalUid=hospital_Uid, doctorUid=time)
    office = ticketList[0].office if ticketList else ''

    for i in ListWSDL().listDoctors(hospital_Uid):
        if i.uid == time:
            doctor = ' '.join([i.name.lastName, i.name.firstName, i.name.patronymic]) # ФИО врача
            db.set('doctor', doctor)

    times = [] # Список времен начала записи текущей недели
    dates = [] # Список дат текущей недели

    for i in xrange(7):
        newDay = firstweekday + datetime.timedelta(days=i)
        dates.append(newDay)
        for j in ticketList:
            if newDay == j.start.date():
                times.append(j.start.time())
        times = list(set(times))
        times.sort()

    ticketTable = []
    if times:
        currentTicketList = []
        for i in ticketList:
            if i.start.date() in dates:
                currentTicketList.append(i)
        for i in times:
            add_to_table = False
            tmp_list = [0]*7
            for j in currentTicketList:
                if j.status in ('free', 'locked'):
                    add_to_table = True
                if j.start.time() == i:
                    tmp_list[dates.index(j.start.date())] = j

            if add_to_table:
                ticketTable.append(tmp_list)

    db.set({'time': time,
            'firstweekday': firstweekday,
            'step': 4})

    return render_to_response(templateName, {'dates': dates,
                                              'times': times,
                                              'office': office,
                                              'ticketTable': ticketTable,
                                              'now': timezone.localtime(timezone.now()).replace(tzinfo=None),
                                            },
                                              context_instance=RequestContext(request))


def patientPage(request, templateName):
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


    def get_captcha_form(data = {}):
        class CaptchaForm(forms.Form):
            captcha = CaptchaField()
        f = CaptchaForm(data, auto_id = True)
        return f

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
            policy1 = request.POST.get('policy1', '').strip()
            policy2 = request.POST.get('policy2', '').strip()
            if not policy2:
                errors.append(u"Введите серию и номер полиса")
            # электронная почта
            userEmail = request.POST.get('email', '')
            if userEmail and not emailValidation(userEmail):
                errors.append(u'Введите корректно адрес электронной почты')

            form = get_captcha_form(request.POST)
            if not form.is_valid():
                errors.append(u'Введёно неверное значение проверочного выражения')

            ticketPatient_err = ''
            # если ошибок в форме нет
            if not errors:
                hospital_Uid = db.get('hospital_Uid')
                time = db.get('time')
                omiPolicyNumber = ' '.join([policy1,policy2])
                patientName = ' '.join([lastName,firstName,patronymic])
                ticketPatient = ScheduleWSDL().enqueue(
                    person = {'lastName': unicode(lastName),
                              'firstName': unicode(firstName),
                              'patronymic': unicode(patronymic)},
                    omiPolicyNumber = unicode(omiPolicyNumber),
                    hospitalUid = hospital_Uid,
                    doctorUid = time,
                    timeslotStart = str(date) + 'T' + str(start_time),
                    hospitalUidFrom = unicode("0"),
                    birthday = unicode('-'.join([yy,mm,dd]))
                )
                # запись на приём произошла успешно:
                if ticketPatient['result'] == 'true' and len(ticketPatient['ticketUid'].split('/')[0]) != 0:
                    db.set({'ticketUid': ticketPatient['ticketUid'],
                             'date': date,
                             'start_time': start_time,
                             'finish_time': finish_time,
                             'omiPolicyNumber': omiPolicyNumber,
                             'patientName': patientName,
                             'birthday': '.'.join([dd,mm,yy])})
                    # формирование и отправка письма:
                    if userEmail:
                        emailLPU = db.get('current_lpu_email')
                        plaintext = get_template('email/email.txt')
                        htmly     = get_template('email/email.html')

                        context = Context({ 'ticketUid': ticketPatient['ticketUid'],
                                            'patientName': db.get('patientName'),
                                            'birthday': db.get('birthday'),
                                            'omiPolicyNumber': db.get('omiPolicyNumber'),
                                            'current_lpu_title': db.get('current_lpu_title'),
                                            'current_lpu_phone': db.get('current_lpu_phone'),
                                            'address': db.get('address'),
                                            'doctor': db.get('doctor'),
                                            'speciality': db.get('speciality'),
                                            'date': date,
                                            'start_time': start_time,
                                            'finish_time': finish_time })

                        subject, from_email, to = u'Уведомление о записи на приём', emailLPU, userEmail
                        text_content = plaintext.render(context)
                        html_content = htmly.render(context)
                        connection = get_connection(settings.EMAIL_BACKEND, False,
                            **{'host':config_value('Mail','EMAIL_HOST'),
                             'port':config_value('Mail','EMAIL_PORT'),
                             'username':config_value('Mail','EMAIL_HOST_USER'),
                             'password':config_value('Mail','EMAIL_HOST_PASSWORD'),
                             'use_tls':config_value('Mail','EMAIL_USE_TLS'),
                             })
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to], connection = connection,)
                        msg.attach_alternative(html_content, "text/html")
                        try:
                            msg.send()
                        except:
                            logger.error("Couldn't connect to smtp")


                    return HttpResponseRedirect(reverse('register'))
                # ошибка записи на приём:
                else:
                    if ticketPatient['result'] == 'true':
                        ticketPatient_err = "Ошибка записи"
                    else:
                        ticketPatient_err = ticketPatient['result']
            # ошибка при записи на приём или ошибки в заполненной форме:
            db.set('step', 5)
            return render_to_response(templateName, {'errors': errors,
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
                                                      'captcha': get_captcha_form()['captcha']
                                                      },
                                                      context_instance=RequestContext(request))
        # если представление было вызвано нажатием на ячейку таблицы на странице Время:
        db.set('step', 5)
        return render_to_response(templateName, {'errors': errors,
                                                  'ticket': ticket,
                                                  'date': date,
                                                  'start_time': start_time,
                                                  'finish_time': finish_time,
                                                  'captcha': get_captcha_form()['captcha']},
                                                  context_instance=RequestContext(request))
    # обращение к форме через адресную строку:
    else:
        return HttpResponseRedirect(reverse('index'))

def registerPage(request, templateName):
    """Логика страницы Запись
    Запись на приём прошла успешно. Здесь происходит запрос на получение сведений о записи (номер талона, имя врача,
    название ЛПУ и т.д.). Далее эти данные передаются в шаблон для вывода на экран и на печать, при необходимости.

    """
    db = Redis(request)
    d = db.get('date').split('-')
    date = datetime.date(int(d[0]),int(d[1]),int(d[2]))
    db.set('step', 6)
    return render_to_response(templateName, {'ticketUid': db.get('ticketUid'),
                                              'date': date,
                                              'start_time': db.get('start_time'),
                                              'finish_time': db.get('finish_time'),
                                              'omiPolicyNumber': db.get('omiPolicyNumber'),
                                              'patientName': db.get('patientName'),
                                              'birthday': db.get('birthday')},
                                              context_instance=RequestContext(request))


##### Представления, используемые AJAX'ом: #####

def updatesPage(request):
    """ Логика страницы updates
    Представление создано только для динамической подгрузки данных при помощи AJAX'а. Вызывается на вкладке
    "Подразделение/Специализация/Врач". Возвращает ответ в формате JSON. Запуск через адресную строку приведет к
    редиректу на главную страницу.

    """
    db = Redis(request)
    data = []
    # при щелчке на элементе из таблицы со списком подразделений:
    if 'clickSpec' in request.GET:
        spec = request.GET['clickSpec']
        hospital_Uid = '/'.join([db.get('sub'), spec])
        doctors_list = ListWSDL().listDoctors(hospital_Uid)
        db.set({'address': request.GET['value'],
                 'spec': spec})
        for i in doctors_list:
            if i.hospitalUid == hospital_Uid:
                data.append(i.speciality)
                data = list(set(data))
                data.sort()

    # при щелчке на элементе из таблицы со списком специализаций:
    elif 'clickProf' in request.GET:
        speciality = request.GET['clickProf']
        hospital_Uid = '/'.join([db.get('sub'), db.get('spec')])
        db.set({'speciality': speciality,
                 'hospital_Uid': hospital_Uid})
        doctors_list = ListWSDL().listDoctors(hospital_Uid = hospital_Uid, speciality = speciality)
        for i in doctors_list:
            if i.hospitalUid == hospital_Uid and i.speciality == speciality:
                data.append({'uid': i.uid, 'name': ' '.join([i.name.lastName, i.name.firstName, i.name.patronymic])})

    # при обращении к странице через адресную строку:
    else:
        return HttpResponseRedirect(reverse('index'))

    # создание ответа в формате json:
    return HttpResponse(json.dumps(data), mimetype='application/json')


def searchPage(request):
    """ Логика страницы search
    Представление создано только для динамической подгрузки данных при помощи AJAX'а. Вызывается на вкладке "ЛПУ".
    Предназначена для поиска ЛПУ по его названию или части названия, по названию или части названия города в котором
    оно находится, по названию или части названия района в котором оно находится. Возвращает ответ в формате JSON.
    Запуск через адресную строку приведет к редиректу на главную страницу.

    """

    def searchMethod(region_list, search_input, result=0):
        """
        Метод применяется для поиска ЛПУ по названию города или по названию района в зависимости от того, что
        передается в переменной region_list.

        """
        tmp_list, tmp_dict, lpu_dict = [], {}, {}
        # получение списка введенных пользователем слов
        search_list = search_input.lower().split(' ')

        # формирование временного списка кортежей [(регион, код ОКАТО), ...]
        for i in region_list:
            tmp_list.append((i.region.lower(), i.code))

        # формирование словаря result со значениями, удовлетворяющими поиску,
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
        return result


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
                # формирование списка доступных городов:
                region_list = Region.objects.filter(activation=True).exclude(region__iendswith=u'район')
                # формирование словаря со значениями, удовлетворяющими поиску,
                # где ключ - uid ЛПУ, а значение - наименование ЛПУ
                result = searchMethod(region_list, search_gorod, result)

            ### поиск ЛПУ по названию района: ###
            if search_rayon:
                # формирование списка доступных районов:
                region_list = Region.objects.filter(activation=True, region__iendswith=u'район')
                # формирование словаря со значениями, удовлетворяющими поиску,
                # где ключ - uid ЛПУ, а значение - наименование ЛПУ
                result = searchMethod(region_list, search_rayon, result)

            # создание ответа в формате json из содержимого словаря result:
            return HttpResponse(json.dumps(result), mimetype='application/json')

    # при обращении к странице через адресную строку:
    else:
        return HttpResponseRedirect(reverse('index'))
