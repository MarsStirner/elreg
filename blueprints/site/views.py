# -*- coding: utf-8 -*-
from flask import (render_template,
                   template_rendered,
                   abort,
                   request,
                   redirect,
                   url_for,
                   flash,
                   session,
                   jsonify)
from jinja2 import Environment, PackageLoader
from datetime import datetime, timedelta, date
from pytz import timezone
from dateutil.tz import tzlocal

from jinja2 import TemplateNotFound
from forms import EnqueuePatientForm

from .app import module
from .lib.service_client import List, Info, Schedule
from .lib.data import del_session, get_doctor_info, get_doctors_with_tickets, get_lpu, save_ticket
from .lib.data import prepare_doctors, search_lpu
from .context_processors import header
from application.app import db
from application.models import Tickets

from .lib.utils import _config, logger
from emails import send_ticket


@module.route('/', methods=['GET'])
def index():
    """ Логика страницы МО
    Главная страница сайта. На ней происходит проверка на наличие у пользователя идентификатора сессии
    и создание сессии пользователя в случае отсутствия идентификатора. А также происходит получение
    списка доступных регионов, установленных в административном интерфейсе.

    """
    # получение списка регионов:
    region_list = List().listRegions()
    session.clear()
    session['step'] = 1
    return render_template('{0}/index.html'.format(module.name), region_list=region_list)


@module.route('/medical_institution/', methods=['GET'])
@module.route('/medical_institution/<okato>/', methods=['GET'])
def lpu(okato=None):
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
def search_lpu():
    session['step'] = 0
    return render_template('{0}/search_lpu.html'.format(module.name))


@module.route('/search/', methods=['GET', 'POST'])
@module.route('/search/<okato>/', methods=['GET', 'POST'])
@module.route('/search/<okato>/<int:lpu_id>/', methods=['GET', 'POST'])
def search(okato=None, lpu_id=None):
    session['step'] = 1
    region_list = List().listRegions()
    if not okato:
        okato = 0
    else:
        session['step'] = 2
    if lpu_id:
        session['step'] = 3
    hospitals = list()
    hospitals_list = List().listHospitals(okato)
    if hospitals_list:
        for _lpu in hospitals_list:
            tmp = _lpu.uid.split('/')
            lpu_id, department_id = int(tmp[0]), int(tmp[1])
            if department_id == 0:
                setattr(_lpu, 'id', lpu_id)
                hospitals.append(_lpu)

    return render_template('{0}/search.html'.format(module.name),
                           region_list=region_list,
                           hospitals=hospitals)


@module.route('/medical_institution/ajax_search/', methods=['GET'])
def ajax_search():
    search_lpu = request.args.get('search_lpu', '')
    search_gorod = request.args.get('search_gorod', '')
    search_rayon = request.args.get('search_rayon', '')
    # если содержимое полей поиска не пустое:
    if search_lpu or search_gorod or search_rayon:
        result = {}

        ### поиск ЛПУ по названию: ###
        if search_lpu:
            tmp_list = []
            # получение списка введенных пользователем слов
            search_list = search_lpu.lower().split(' ')

            # формирование временного списка кортежей [(uid ЛПУ, наименование ЛПУ), ...]
            for i in Info().getHospitalInfo():
                tmp_list.append((i.uid.split('/')[0], i.name.lower()))
            # формирование словаря со значениями, удовлетворяющими поиску,
            # где ключ - uid ЛПУ, а значение - наименование ЛПУ
            for (uid, title) in tmp_list:
                flag = True
                for i in search_list:
                    if title.find(i) == -1:
                        flag = False
                if flag:
                    result[uid] = title

        ### поиск ЛПУ по названию города: ###
        if search_gorod:
            # формирование списка доступных городов:
            # region_list = Region.objects.filter(activation=True).exclude(region__iendswith=u'район')
            region_list = []
            for region in List().listRegions():
                if region.name.find(u'район') == -1:
                    region_list.append(region)
            # формирование словаря со значениями, удовлетворяющими поиску,
            # где ключ - uid ЛПУ, а значение - наименование ЛПУ
            result = search_lpu(region_list, search_gorod, result)

        ### поиск ЛПУ по названию района: ###
        if search_rayon:
            # формирование списка доступных районов:
            # region_list = Region.objects.filter(activation=True, region__iendswith=u'район')
            region_list = []
            for region in List().listRegions():
                if region.name.find(u'район') > 0:
                    region_list.append(region)
            # формирование словаря со значениями, удовлетворяющими поиску,
            # где ключ - uid ЛПУ, а значение - наименование ЛПУ
            result = search_lpu(region_list, search_rayon, result)

        # создание ответа в формате json из содержимого словаря result:
        return jsonify(result)


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
    now = datetime.now(tzlocal()).astimezone(tz=timezone(_config('TIME_ZONE'))).replace(tzinfo=None)
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

    doctor_info = get_doctor_info(hospital_uid, doctor_id)

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

    session['lpu_id'] = lpu_id
    session['department_id'] = department_id
    session['doctor_id'] = doctor_id

    if request.args.get('office'):
        session['office'] = request.args.get('office')

    if 'doctor' not in session:
        session['doctor'] = get_doctor_info(hospital_uid, doctor_id)

    timeslot, ticket_start, ticket_end = None, None, None

    date_string = '{date}{time}'.format(date=request.args.get('d'), time=request.args.get('s'))
    try:
        timeslot = datetime.strptime(date_string, '%Y%m%d%H%M%S').replace(tzinfo=timezone(_config('TIME_ZONE')))
        ticket_start = datetime.strptime(request.args.get('s'), '%H%M%S').time()
        ticket_end = datetime.strptime(request.args.get('f'), '%H%M%S').time()
    except Exception, e:
        print e
        abort(404)

    session['step'] = 5

    form = EnqueuePatientForm(request.form, **dict(session))
    if request.method == 'POST':
        session.update(form.data)
    if form.validate_on_submit():
        document_type = form.document_type.data.strip()
        document = dict()
        if not document_type:
            flash(u"Выберите тип документа", 'error')
        else:
            if document_type in ('policy_type_2', 'policy_type_3'):
                document['policy_type'] = int(document_type.replace('policy_type_', ''))
                document['series'] = form.series.data.strip()
                document['number'] = form.number.data.strip()
            elif document_type in ('doc_type_4', 'doc_type_7'):
                document['document_code'] = int(document_type.replace('doc_type_', ''))
                document['series'] = form.doc_series.data.strip()
                document['number'] = form.doc_number.data.strip()
            elif document_type == 'client_id':
                document['client_id'] = int(form.client_id.data.strip())
            elif document_type in ('policy_type_1', 'policy_type_4'):
                document['policy_type'] = int(document_type.replace('policy_type_', ''))
                document['number'] = form.policy_number.data.strip()

        # электронная почта
        patient_email = form.email.data.strip()
        send_email = form.send_email.data

        ticket = Schedule().enqueue(
            person={'lastName': unicode(form.lastname.data.strip().title()),
                    'firstName': unicode(form.firstname.data.strip().title()),
                    'patronymic': unicode(form.patronymic.data.strip().title())},
            document=document,
            sex=form.gender.data,
            hospitalUid=hospital_uid,
            doctorUid=doctor_id,
            timeslotStart=timeslot.strftime('%Y-%m-%dT%H:%M:%S'),
            hospitalUidFrom='',
            birthday=unicode('{year}-{month}-{day}'.format(**form.data))
        )

        patient = dict(name=u'{lastname} {firstname} {patronymic}'.format(**form.data),
                       birthday=u'{day:02d}.{month:02d}.{year}'.format(**form.data))

        # запись на приём произошла успешно:
        if ticket and getattr(ticket, 'result', False) is True and len(ticket.ticketUid.split('/')[0]) != 0:
            #doc_keys = ('policy_type', 'policy_number', 'doc_series', 'doc_number', 'client_id', 'series', 'number')
            #[_del_session(key) for key in doc_keys]

            session['ticket_uid'] = ticket.ticketUid
            session['date'] = timeslot.date().strftime('%d.%m.%Y')
            session['start_time'] = ticket_start.strftime('%H:%M')
            session['finish_time'] = ticket_end.strftime('%H:%M')

            session['document'] = document
            session['patient'] = patient

            ticket_hash = save_ticket(ticket.ticketUid, lpu_info=lpu_info)
            session['ticket_hash'] = ticket_hash

            # формирование и отправка письма:
            if send_email and patient_email:
                dequeue_link = '{0}://{1}{2}'.format(request.scheme,
                                                     request.host,
                                                     url_for('.dequeue',
                                                             lpu_id=session.get('lpu_id'),
                                                             department_id=session.get('department_id'),
                                                             uid=ticket_hash))
                send_ticket(patient_email, form.data, lpu_info, dequeue_link=dequeue_link, session_data=session)

            log_message = render_template('{0}/messages/success.txt'.format(module.name),
                                          lpu=lpu_info,
                                          lpu_id=lpu_id,
                                          doctor_id=doctor_id,
                                          doctor=session['doctor'],
                                          patient_id=ticket.ticketUid.split('/')[1],
                                          ticket_id=ticket.ticketUid.split('/')[0],
                                          patient=patient,
                                          date=timeslot.date().strftime('%d.%m.%Y'),
                                          start_time=ticket_start.strftime('%H:%M'),
                                          finish_time=ticket_end.strftime('%H:%M'))
            logger.info(log_message, extra=dict(tags=[u'успешная запись', 'elreg']))

            return redirect(url_for('.ticket_info'))
        elif ticket and hasattr(ticket, 'result'):
            # ошибка записи на приём:
            if ticket.result is True:
                flash(u"Ошибка записи", 'error')
                log_message = render_template('{0}/messages/failed.txt'.format(module.name),
                                              lpu=lpu_info,
                                              lpu_id=lpu_id,
                                              doctor_id=doctor_id,
                                              doctor=session['doctor'],
                                              patient=patient,
                                              message=u"Ошибка записи",
                                              date=timeslot.date().strftime('%d.%m.%Y'),
                                              start_time=ticket_start.strftime('%H:%M'),
                                              finish_time=ticket_end.strftime('%H:%M'))
                logger.error(log_message, extra=dict(tags=[u'ошибка записи', 'elreg']))
            else:
                flash(ticket.message, 'error')
                log_message = render_template('{0}/messages/failed.txt'.format(module.name),
                                              lpu=lpu_info,
                                              lpu_id=lpu_id,
                                              doctor_id=doctor_id,
                                              doctor=session['doctor'],
                                              patient=patient,
                                              message=ticket.message,
                                              date=timeslot.date().strftime('%d.%m.%Y'),
                                              start_time=ticket_start.strftime('%H:%M'),
                                              finish_time=ticket_end.strftime('%H:%M'))
                logger.error(log_message, extra=dict(tags=[u'ошибка записи', 'elreg']))
        else:
            flash(u'Не удалось соединиться с сервером. Попробуйте отправить запрос ещё раз.', 'error')
            log_message = render_template('{0}/messages/failed.txt'.format(module.name),
                                          lpu=lpu_info,
                                          lpu_id=lpu_id,
                                          doctor_id=doctor_id,
                                          patient=patient,
                                          doctor=session['doctor'],
                                          message=getattr(ticket, 'message', u'Не удалось соединиться с ИС'),
                                          date=timeslot.date().strftime('%d.%m.%Y'),
                                          start_time=ticket_start.strftime('%H:%M'),
                                          finish_time=ticket_end.strftime('%H:%M'))
            logger.error(log_message, extra=dict(tags=[u'ошибка записи', 'elreg']))

        # если представление было вызвано нажатием на ячейку таблицы на странице Время:
    return render_template('{0}/registration.html'.format(module.name),
                           lpu=lpu_info,
                           date=timeslot.date(),
                           start_time=ticket_start,
                           finish_time=ticket_end,
                           office=session.get('office'),
                           doctor=session.get('doctor'),
                           form=form)


@module.route('/register/', methods=['GET'])
def ticket_info():
    session['step'] = 6
    hospital_uid = '{0}/{1}'.format(session.get('lpu_id'), session.get('department_id'))
    lpu_info = get_lpu(hospital_uid)
    return render_template('{0}/ticket_info.html'.format(module.name), lpu=lpu_info)


@module.route('/ajax_lpu/', methods=['GET'])
@module.route('/ajax_lpu/<okato>', methods=['GET'])
def get_lpu_list(okato=None):
    data = list()
    lpu_list = List().listHospitals(okato)
    if lpu_list:
        for _lpu in lpu_list:
            data.append(dict(id=_lpu.uid.split('/')[0],
                             name=_lpu.name))
    return jsonify(result=data)


@module.route('/ajax_specialities/', methods=['GET'])
@module.route('/ajax_specialities/<int:lpu_id>/<int:department_id>/', methods=['GET'])
def get_specialities(lpu_id, department_id):
    if not lpu_id or not department_id:
        abort(404)
    data = list()
    doctors = List().listDoctors(hospital_Uid='{0}/{1}'.format(lpu_id, department_id))
    for doctor in getattr(doctors, 'doctors', []):
        # TODO: не нужно ли свести к ordered dict(id=>value)??
        #if doctor.hospitalUid == hospital_Uid:
        data.append(doctor.speciality)
        data = list(set(data))
        data.sort()
    return jsonify(result=data)


@module.route('/ajax_lpu_doctors/', methods=['GET'])
@module.route('/ajax_lpu_doctors/<int:lpu_id>/', methods=['GET'])
def get_lpu_doctors(lpu_id=None):
    speciality = request.args.get('sp')
    if not lpu_id:
        abort(404)
    hospital_uid = '{0}/0'.format(lpu_id)
    params = dict(hospital_Uid=hospital_uid)
    if speciality:
        params['speciality'] = speciality
    doctors = List().listDoctors(**params)
    data = prepare_doctors(doctors)
    return jsonify(result=data)


@module.route('/ajax_lpu_specialities/', methods=['GET'])
@module.route('/ajax_lpu_specialities/<int:lpu_id>/', methods=['GET'])
def get_lpu_specialities(lpu_id=None):
    if not lpu_id:
        abort(404)
    specialities = list()
    _doctors = List().listDoctors(hospital_Uid='{0}/0'.format(lpu_id))
    for doctor in getattr(_doctors, 'doctors', []):
        specialities.append(doctor.speciality)
    specialities = list(set(specialities))
    specialities.sort()
    doctors = prepare_doctors(_doctors)
    return jsonify(specialities=specialities, doctors=doctors)


@module.route('/ajax_find_doctors/', methods=['POST'])
@module.route('/ajax_find_doctors/<int:lpu_id>/', methods=['POST'])
def find_doctors(lpu_id=None):
    # TODO: желательно перейти от наименования специальности к id
    speciality = request.values.get('sp')
    fio = request.values.get('fio', '')
    lastName = fio.split(' ')[0].strip()
    params = dict()
    if lpu_id:
        params['hospital_Uid'] = '{0}/0'.format(lpu_id)
    if speciality:
        params['speciality'] = speciality
    if lastName:
        params['lastName'] = lastName
    data = list()
    doctors = List().listDoctors(**params)
    if doctors:
        data = prepare_doctors(doctors)
    return jsonify(result=data)


@module.route('/ajax_doctors/<int:lpu_id>/<int:department_id>/', methods=['GET'])
def get_doctors(lpu_id=None, department_id=None):
    # TODO: желательно перейти от наименования специальности к id
    speciality = request.args.get('sp')
    if not lpu_id or not department_id or not speciality:
        abort(404)
    hospital_uid = '{0}/{1}'.format(lpu_id, department_id)
    data = get_doctors_with_tickets(hospital_Uid=hospital_uid,
                                     speciality=speciality)
    return jsonify(result=data)


@module.route('/dequeue/<int:lpu_id>/<int:department_id>/<uid>/', methods=['GET', 'POST'])
def dequeue(lpu_id, department_id, uid):
    ticket = db.session.query(Tickets).filter(Tickets.uid == uid, Tickets.is_active == True).first()
    if not ticket:
        abort(404)
    del_session('step')
    ticket_info = ticket.info
    ticket_id, patient_id = ticket.ticket_uid.split('/')
    if request.method == 'POST':
        result = Schedule().dequeue(hospitalUid='{0}/{1}'.format(lpu_id, department_id),
                                    ticketUid=ticket.ticket_uid)
        if result and result['success']:
            flash(u'Отмена записи произведена успешно', category='success')
            ticket.is_active = False
            ticket.updated = datetime.now()
            db.session.commit()
            log_message = render_template('{0}/messages/dequeue.txt'.format(module.name),
                                          ticket_info=ticket_info,
                                          patient_id=patient_id,
                                          ticket_id=ticket_id,
                                          message=u'Произведена отмена записи')
            logger.info(log_message, extra=dict(tags=[u'отмена записи', 'elreg']))
        elif result:
            flash(u'''Запись не существует или уже отменена''', category='error')
            ticket.is_active = False
            ticket.updated = datetime.now()
            db.session.commit()
            log_message = render_template('{0}/messages/dequeue.txt'.format(module.name),
                                          ticket_info=ticket_info,
                                          patient_id=patient_id,
                                          ticket_id=ticket_id,
                                          message=u'Запись не существует или отменена ранее')
            logger.info(log_message, extra=dict(tags=[u'отмена записи', 'elreg']))
        else:
            flash(u'''Отмена записи произошла с ошибкой,
                  <a href="{0}">попробуйте ещё раз</a>
                  или сообщите об отмене записи лечебному учреждению по контактным данным,
                  указанным в талоне'''
                  .format(url_for('.dequeue', lpu_id=lpu_id, department_id=department_id, uid=uid)), category='error')

            log_message = render_template('{0}/messages/dequeue.txt'.format(module.name),
                                          ticket_info=ticket_info,
                                          patient_id=patient_id,
                                          ticket_id=ticket_id,
                                          message=u'Ошибка отмены записи')
            logger.error(log_message, extra=dict(tags=[u'отмена записи', 'elreg']))
    return render_template('{0}/dequeue.html'.format(module.name), ticket_info=ticket_info)


@module.errorhandler(404)
def page_not_found(e):
    return render_template('{0}/404.html'.format(module.name)), 404
