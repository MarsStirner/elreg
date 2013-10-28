# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash, session, current_app, jsonify
import math
from datetime import datetime, timedelta, date
from pytz import timezone

from jinja2 import TemplateNotFound
from forms import EnqueuePatientForm

from .app import module
from .lib.service_client import List, Info, Schedule
from .context_processors import header

from .lib.utils import _config, stringValidation


@module.route('/', methods=['GET'])
def index():
    """ Логика страницы МО
    Главная страница сайта. На ней происходит проверка на наличие у пользователя идентификатора сессии
    и создание сессии пользователя в случае отсутствия идентификатора. А также происходит получение
    списка доступных регионов, установленных в административном интерфейсе.

    """
    # получение списка регионов:
    region_list = List().listRegions()
    session['step'] = 1

    return render_template('{0}/index.html'.format(module.name), region_list=region_list,
                           break_keys=(math.ceil(len(region_list) / 3.), math.ceil(2 * len(region_list) / 3.),))


@module.route('/medical_institution/', methods=['GET'])
@module.route('/medical_institution/<okato>/', methods=['GET'])
def lpu(okato):
    """ Логика страницы ЛПУ
    Из полученного кода ОКАТО находим список всех ЛПУ для данного региона. Если на страницу попадаем через
    кнопку "Поиск ЛПУ", тогда  в okato передается строка search и список ЛПУ не выводится.
    """
    # if not okato:
    #     # в случае прямого перехода на страницу
    #     return HttpResponseRedirect(reverse('index'))
    session['step'] = 2
    session['okato'] = okato
    hospitals_list = list()
    if okato != "search":
        hospitals_list = List().listHospitals(okato)  # список ЛПУ выбранного региона
        for hospital in hospitals_list:
            hospital.uid = hospital.uid.split('/')[0]
    return render_template('{0}/lpu.html'.format(module.name), hospitals_list=hospitals_list)


@module.route('/medical_institution/search/', methods=['GET'])
def search():
    return render_template('{0}/lpu.html'.format(module.name))


@module.route('/division/', methods=['GET'])
@module.route('/division/<int:lpu_id>/', methods=['GET'])
def division(lpu_id=None):
    """Логика страницы Подразделение/Специализация/Врач
    Выводится список подразделений для выбранного ЛПУ. Остальная логика
    """
    session['step'] = 3
    session['lpu_id'] = lpu_id
    lpu_info = get_lpu('{0}/0'.format(lpu_id))

    return render_template('{0}/division.html'.format(module.name),
                           lpu_id=lpu_id,
                           lpu=lpu_info)


@module.route('/time/<int:lpu_id>/<int:department_id>/<int:doctor_id>/', methods=['GET'])
@module.route('/time/<int:lpu_id>/<int:department_id>/<int:doctor_id>/<start>/', methods=['GET'])
def tickets(lpu_id, department_id, doctor_id, start=None):
    session['step'] = 4
    session['lpu_id'] = lpu_id
    session['department_id'] = department_id
    session['doctor_id'] = doctor_id

    hospital_uid = '{0}/{1}'.format(lpu_id, department_id)
    lpu_info = get_lpu(hospital_uid)

    today = date.today()
    now = datetime.now()
    monday = None

    if start is not None:
        try:
            monday = datetime.strptime(start, '%Y%m%d').date()
        except ValueError, e:
            print e
    if monday is None:
        monday = today - timedelta(days=date.isoweekday(today) - 1)

    tickets = Schedule().getScheduleInfo(hospitalUid=hospital_uid,
                                         doctorUid=doctor_id,
                                         startDate=monday,
                                         endDate=monday+timedelta(days=6))
    office = None
    if tickets:
        office = getattr(tickets[0], 'office', '')

    # TODO: хорошо бы иметь метод получения врача по uid
    doctors = List().listDoctors(hospital_Uid=hospital_uid)

    doctor_info = None
    for doctor in doctors:
        if doctor_id and doctor.uid == doctor_id:
            doctor_info = dict(firstName=doctor.name.firstName,
                               lastName=doctor.name.lastName,
                               patronymic=doctor.name.patronymic,
                               speciality=doctor.speciality)
            break

    times = []  # Список времен начала записи текущей недели
    dates = []  # Список дат текущей недели

    for i in xrange(7):
        new_day = monday + timedelta(days=i)
        dates.append(new_day)
        if tickets:
            for j in tickets:
                if new_day == j.start.date():
                    times.append(j.start.time())
        times = list(set(times))
        times.sort()

    ticket_table = []
    if times:
        current_ticket_list = []
        if tickets:
            for i in tickets:
                if i.start.date() in dates:
                    current_ticket_list.append(i)
        for i in times:
            add_to_table = False
            tmp_list = [0] * 7
            for j in current_ticket_list:
                if j.start.time() == i:
                    tmp_list[dates.index(j.start.date())] = j
                    if j.start > now and j.status in ('free', 'locked', 'disabled'):
                        add_to_table = True

            if add_to_table:
                ticket_table.append(tmp_list)

    session['doctor'] = doctor_info
    session['office'] = office
    return render_template('{0}/tickets.html'.format(module.name),
                           dates=dates,
                           times=times,
                           lpu=lpu_info,
                           lpu_id=lpu_id,
                           department_id=department_id,
                           doctor_id=doctor_id,
                           doctor=doctor_info,
                           office=office,
                           ticket_table=ticket_table,
                           prev_monday=(monday - timedelta(days=7)).strftime('%Y%m%d'),
                           next_monday=(monday + timedelta(days=7)).strftime('%Y%m%d'),
                           #now=datetime.now(tz=timezone(_config('TIME_ZONE'))),
                           now=now)


@module.route('/patient/<int:lpu_id>/<int:department_id>/<int:doctor_id>/', methods=['POST', 'GET'])
def registration(lpu_id, department_id, doctor_id):
    """Логика страницы Запись на приём
    Здесь происходит обработка данных полученных от пользователя (на стороне сервера). Осуществляется проверка на
    наличие незаполненных полей и упрощенная валидация введенных данных. Все найденные ошибки заносятся в
    словарь errors, который выводится в шаблон в случае присутствия в нем элементов. В случае отсутствия ошибок в
    форме с данными пользователя формируется запрос на запись в ЛПУ (ticketPatient). При отклонении записи на приём,
    причина отклонения содержится в переменной result, которая и передается в шаблон. При успешной записи на приём,
    в случае если пользователь указал e-mail (userEmail), формируется тело письма и выполняется его отправка. Далее
    осуществляется редирект на страницу Запись.

    """
    hospital_uid = '{0}/{1}'.format(lpu_id, department_id)
    lpu_info = get_lpu(hospital_uid)
    session['step'] = 5

    errors = []
    ticket_date = datetime.strptime(request.args.get('d'), '%Y%m%d').replace(tzinfo=timezone(_config('TIME_ZONE')))
    ticket_start = datetime.strptime(request.args.get('s'), '%H%M').replace(tzinfo=timezone(_config('TIME_ZONE')))
    ticket_end = datetime.strptime(request.args.get('f'), '%H%M').replace(tzinfo=timezone(_config('TIME_ZONE')))

    form = EnqueuePatientForm(request.form)
    if form.validate_on_submit():
        pass




    # если представление было вызвано при нажатии кнопки submit на странице Пациент:
    if request.form.get('flag', ''):
        # Проверка на заполненность формы пользователем и ее корректность:
        # фамилия
        lastName = request.form.get('lastName', '').strip()
        if not lastName:
            flash(u"Введите фамилию", 'error')
        elif not stringValidation(lastName):
            flash(u'Введите корректно фамилию', 'error')
        # имя
        firstName = request.form.get('firstName', '').strip()
        if not firstName:
            flash(u"Введите имя", 'error')
        elif not stringValidation(firstName):
            flash(u'Введите корректное имя', 'error')
        # отчество
        patronymic = request.form.get('patronymic', '').strip()
        if not patronymic:
            flash(u"Введите отчество", 'error')
        elif not stringValidation(patronymic):
            flash(u'Введите корректно отчество', 'error')
        # день рождения
        dd = request.form.get('dd', '').strip()
        mm = request.form.get('mm', '').strip()
        yy = request.form.get('yy', '').strip()
        if not dd or not mm or not yy:
            flash(u'Введите дату рождения', 'error')
        # документ
        document_type = request.form.get('document_type', '').strip()
        series = request.form.get('series', '').strip()
        number = request.form.get('number', '').strip()
        doc_meta_type = ''

        document = dict()
        if not document_type:
            flash(u"Выберите тип документа", 'error')
        else:
            if document_type in ('policy_type_2', 'policy_type_3'):
                doc_meta_type = 'oms_dms'
                document['policy_type'] = int(document_type.replace('policy_type_', ''))
                document['series'] = series
                document['number'] = number
            elif document_type in ('doc_type_4', 'doc_type_7'):
                doc_meta_type = 'doc'
                document['document_code'] = int(document_type.replace('doc_type_', ''))
                document['series'] = series
                document['number'] = number
            elif document_type == 'client_id':
                doc_meta_type = 'amb'
                document['client_id'] = int(number)
            elif document_type == 'policy_type_4':
                doc_meta_type = 'new_oms'
                document['policy_type'] = int(document_type.replace('policy_type_', ''))
                document['number'] = number

            if not number:
                flash(u"Введите номер документа", 'error')

        # электронная почта
        userEmail = request.form.get('email', '').strip()
        if userEmail:
            errors.append(u'Введите корректно адрес электронной почты')

        #form = get_captcha_form(request.form)
        if not form.is_valid():
            flash(u'Введено неверное значение проверочного выражения или истекло время, отведенное для его ввода',
                  'error')

        ticketPatient_err = ''

        _remember_user(request,
                       {'lastName': lastName,
                        'firstName': firstName,
                        'patronymic': patronymic,
                        'dd': dd,
                        'mm': mm,
                        'yy': yy,
                        'document_type': document_type,
                        'doc_meta_type': doc_meta_type,
                        'series': series if series != '0' else '',
                        'number': number,
                        'userEmail': userEmail,
                        'sex': request.form.get('radio', ''),
                        'send_email': request.form.get('send_email', '')})

        # если ошибок в форме нет
        if not errors:
            hospital_uid = db.get('hospital_Uid')
            time = db.get('time')
            patientName = ' '.join([lastName, firstName, patronymic])

            ticketPatient = Schedule().enqueue(
                person={'lastName': unicode(lastName),
                        'firstName': unicode(firstName),
                        'patronymic': unicode(patronymic)},
                document=document,
                sex=request.form.get('radio', ''),
                hospitalUid=hospital_uid,
                doctorUid=time,
                timeslotStart=str(date) + 'T' + str(start_time),
                hospitalUidFrom='',
                birthday=unicode('-'.join([yy, mm, dd]))
            )

            # запись на приём произошла успешно:
            if ticketPatient and ticketPatient.result is True and len(ticketPatient.ticketUid.split('/')[0]) != 0:
                doc_keys = ('policy_type', 'document_code', 'client_id', 'series', 'number')
                db.delete(*doc_keys)
                for key in doc_keys:
                    db.set(key, '0')

                start_time = start_time.strftime('%H:%M')
                finish_time = finish_time.strftime('%H:%M')

                db_params = {'ticketUid': ticketPatient.ticketUid,
                             'date': date,
                             'start_time': start_time,
                             'finish_time': finish_time,
                             'patientName': patientName,
                             'birthday': '.'.join([dd, mm, yy])}
                db_params.update(document)
                db.set(db_params)
                # формирование и отправка письма:
                if userEmail:
                    emailLPU = db.get('current_lpu_email')
                    plaintext = get_template('email/email.txt')
                    htmly = get_template('email/email.html')

                    context_parameters = {'ticketUid': ticketPatient.ticketUid,
                                           'patientName': db.get('patientName'),
                                           'birthday': db.get('birthday'),
                                           'current_lpu_title': db.get('current_lpu_title'),
                                           'current_lpu_phone': db.get('current_lpu_phone'),
                                           'address': db.get('address'),
                                           'doctor': db.get('doctor'),
                                           'speciality': db.get('speciality'),
                                           'date': date,
                                           'start_time': start_time,
                                           'finish_time': finish_time}
                    context_parameters.update(document)
                    context = Context(context_parameters)

                    subject, from_email, to = u'Уведомление о записи на приём', emailLPU, userEmail
                    text_content = plaintext.render(context)
                    html_content = htmly.render(context)
                    connection = get_connection(settings.EMAIL_BACKEND, False,
                                                **{'host': str(config_value('Mail', 'EMAIL_HOST')),
                                                   'port': config_value('Mail', 'EMAIL_PORT'),
                                                   'username': str(config_value('Mail', 'EMAIL_HOST_USER')),
                                                   'password': str(config_value('Mail', 'EMAIL_HOST_PASSWORD')),
                                                   'use_tls': config_value('Mail', 'EMAIL_USE_TLS'),
                                                   })
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to], connection=connection,)
                    msg.attach_alternative(html_content, "text/html")
                    try:
                        msg.send()
                    except Exception, e:
                        print e
                        logger.error(e)

                return HttpResponseRedirect(reverse('register'))
            # ошибка записи на приём:
            elif ticketPatient:
                if ticketPatient.result is True:
                    ticketPatient_err = u"Ошибка записи"
                else:
                    ticketPatient_err = ticketPatient.message
            else:
                ticketPatient_err = '''Не удалось соединиться с сервером.
                Попробуйте отправить запрос ещё раз.'''
        # ошибка при записи на приём или ошибки в заполненной форме:
        db.set('step', 5)

        # если представление было вызвано нажатием на ячейку таблицы на странице Время:
    return render_template('{0}/registration.html'.format(module.name),
                           lpu=lpu_info,
                           date=ticket_date,
                           start_time=ticket_start,
                           finish_time=ticket_end,
                           office=session['office'],
                           doctor=session['doctor'],
                           form=form)


@module.route('/register/', methods=['POST'])
def ticket_info():
    session['step'] = 6
    return render_template('{0}/ticket_info.html'.format(module.name))


@module.route('/ajax_specialities/<int:lpu_id>/<int:department_id>/', methods=['GET'])
def get_specialities(lpu_id, department_id):
    if not lpu_id or not department_id:
        abort(404)
    data = list()
    doctors_list = List().listDoctors(hospital_Uid='{0}/{1}'.format(lpu_id, department_id))
    for doctor in doctors_list:
        # TODO: не нужно ли свести к ordered dict(id=>value)??
        #if doctor.hospitalUid == hospital_Uid:
        data.append(doctor.speciality)
        data = list(set(data))
        data.sort()
    return jsonify(result=data)


@module.route('/ajax_doctors/<int:lpu_id>/<int:department_id>/', methods=['GET'])
def get_doctors(lpu_id=None, department_id=None):
    # TODO: желательно перейти от наименования специальности к id
    speciality = request.args.get('sp')
    if not lpu_id or not department_id or not speciality:
        abort(404)
    data = list()
    hospital_uid = '{0}/{1}'.format(lpu_id, department_id)
    doctors_list = List().listDoctors(hospital_Uid=hospital_uid,
                                      speciality=speciality)
    for doctor in doctors_list:
        if doctor.speciality == speciality:
            _tickets = list()
            closest_tickets = Schedule().get_closest_tickets(hospital_uid, [doctor.uid])
            if closest_tickets:
                for key, value in enumerate(closest_tickets):
                    _tickets.append(dict(href=url_for('.registration',
                                                      lpu_id=lpu_id,
                                                      department_id=department_id,
                                                      doctor_id=doctor.uid,
                                                      d=value['timeslotStart'].strftime('%Y%m%d'),
                                                      s=value['timeslotStart'].strftime('%H%M'),
                                                      f=value['timeslotEnd'].strftime('%H%M')),
                                         info=value['timeslotStart'].strftime('%d.%m %H:%M')))
            data.append(dict(uid=doctor.uid,
                             name=' '.join([doctor.name.lastName, doctor.name.firstName, doctor.name.patronymic]),
                             schedule_href=url_for('.tickets',
                                                   lpu_id=lpu_id,
                                                   department_id=department_id,
                                                   doctor_id=doctor.uid),
                             tickets=_tickets))
    return jsonify(result=data)


def get_lpu(hospital_uid):
    lpu_info = None
    try:
        hospitals = Info().getHospitalInfo(hospitalUid=hospital_uid)
    except Exception, e:
        print e
    else:
        lpu_info = hospitals[0]
        for build in lpu_info.buildings:
            build.name = unicode(build.name)
            build.address = unicode(build.address)
    return lpu_info