# -*- encoding: utf-8 -*-
from flask import (render_template,
                   template_rendered,
                   abort,
                   request,
                   redirect,
                   url_for,
                   flash,
                   session,
                   current_app,
                   jsonify)
from jinja2 import Environment, PackageLoader
from flask_mail import Mail, Message
import math
from datetime import datetime, timedelta, date
from pytz import timezone

from jinja2 import TemplateNotFound
from forms import EnqueuePatientForm

from .app import module
from .lib.service_client import List, Info, Schedule
from .context_processors import header

from .lib.utils import _config


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
    lpu_info = get_lpu('{0}/0'.format(lpu_id))

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

    doctor_info = _get_doctor_info(hospital_uid, doctor_id)

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
    lpu_info = get_lpu('{0}/0'.format(lpu_id))

    session['department_id'] = department_id
    session['doctor_id'] = doctor_id

    if request.args.get('office'):
        session['office'] = request.args.get('office')

    if 'doctor' not in session:
        session['doctor'] = _get_doctor_info(hospital_uid, doctor_id)

    timeslot, ticket_start, ticket_end = None, None, None

    date_string = '{date}{time}'.format(date=request.args.get('d'), time=request.args.get('s'))
    try:
        timeslot = datetime.strptime(date_string, '%Y%m%d%H%M').replace(tzinfo=timezone(_config('TIME_ZONE')))
        ticket_start = datetime.strptime(request.args.get('s'), '%H%M').time()
        ticket_end = datetime.strptime(request.args.get('f'), '%H%M').time()
    except Exception, e:
        print e
        abort(404)

    session['step'] = 5

    form = EnqueuePatientForm(request.form)
    if form.validate_on_submit():
        session.update(form.data)

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
            elif document_type == 'policy_type_4':
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

        # запись на приём произошла успешно:
        if ticket and ticket.result is True and len(ticket.ticketUid.split('/')[0]) != 0:
            #doc_keys = ('policy_type', 'policy_number', 'doc_series', 'doc_number', 'client_id', 'series', 'number')
            #[_del_session(key) for key in doc_keys]

            session['ticket_uid'] = ticket.ticketUid
            session['date'] = timeslot.date().strftime('%d.%m.%Y')
            session['start_time'] = ticket_start.strftime('%H:%M')
            session['finish_time'] = ticket_end.strftime('%H:%M')

            session['document'] = document

            session['patient'] = dict(name=u'{lastname} {firstname} {patronymic}'.format(**form.data),
                                      birthday=u'{day:02d}.{month:02d}.{year}'.format(**form.data))

            # формирование и отправка письма:
            if send_email and patient_email:
                _send_ticket(patient_email, form.data, lpu_info)

            return redirect(url_for('.ticket_info'))
            # ошибка записи на приём:
        elif ticket:
            if ticket.result is True:
                flash(u"Ошибка записи", 'error')
            else:
                flash(ticket.message, 'error')
        else:
            flash(u'Не удалось соединиться с сервером. Попробуйте отправить запрос ещё раз.', 'error')

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
                                                      office=value['office'],
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
        for build in getattr(lpu_info, 'buildings', list()):
            build.name = build.name
            build.address = build.address
    return lpu_info


def _get_doctor_info(hospital_uid, doctor_id):
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
    return doctor_info


def _generate_message(template, data, lpu_info):
    env = Environment(loader=PackageLoader(module.import_name,  module.template_folder))
    template = env.get_template(template)
    return template.render(data=data, session=session, lpu=lpu_info)


def _send_ticket(patient_email, data, lpu_info):
    mail = Mail(current_app)
    message = Message(u'Уведомление о записи на приём', recipients=[patient_email])

    message.body = _generate_message('{0}/email/email.txt'.format(module.name), data, lpu_info)
    message.html = _generate_message('{0}/email/email.html'.format(module.name), data, lpu_info)

    try:
        mail.send(message)
    except Exception, e:
        print e
        return False
    return True


def _del_session(key):
    if key in session:
        del session[key]