# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from dateutil.tz import tzlocal
from flask import url_for, session
from jinja2 import Environment, PackageLoader
from service_client import List, Info, Schedule
from application.app import db
from application.models import Tickets
from ..app import module
from utils import _config, logger


def get_lpu(hospital_uid):
    lpu_info = None
    try:
        hospitals = Info().getHospitalInfo(hospitalUid=hospital_uid)
    except Exception, e:
        print e
    else:
        if len(hospitals) > 0:
            lpu_info = hospitals[0]
        #for build in getattr(lpu_info, 'buildings', list()):
        #    build.name = build.name
        #    build.address = build.address
    return lpu_info


def get_doctor_info(hospital_uid, doctor_id):
    # TODO: хорошо бы иметь метод получения врача по uid
    doctors = List().listDoctors(hospital_Uid=hospital_uid)

    doctor_info = None
    for doctor in getattr(doctors, 'doctors', []):
        if doctor_id and doctor.uid == doctor_id:
            doctor_info = dict(firstName=doctor.name.firstName,
                               lastName=doctor.name.lastName,
                               patronymic=doctor.name.patronymic,
                               speciality=doctor.speciality)
            break
    return doctor_info


def del_session(key):
    if key in session:
        del session[key]


def save_ticket(ticket_uid, lpu_info):
    import hashlib
    uid = hashlib.md5(ticket_uid).hexdigest()
    env = Environment(loader=PackageLoader(module.import_name,  module.template_folder))
    template = env.get_template('{0}/_ticket.html'.format(module.name))
    info = template.render(lpu=lpu_info, session=session)
    ticket = Tickets(uid=uid, ticket_uid=ticket_uid, info=info)
    db.session.add(ticket)
    db.session.commit()
    return uid


def search_lpu(region_list, search_input, result):
    """Поиск ЛПУ по названию города или по названию района в зависимости от того, что
    передается в переменной region_list.

    """
    tmp_list, tmp_dict, lpu_dict = [], {}, {}
    # получение списка введенных пользователем слов
    search_list = search_input.lower().split(' ')

    # формирование временного списка кортежей [(регион, код ОКАТО), ...]
    for i in region_list:
        tmp_list.append((i.name.lower(), i.code))

    # формирование словаря result со значениями, удовлетворяющими поиску,
    # где ключ - uid ЛПУ, а значение - наименование ЛПУ
    for (region, code) in tmp_list:
        flag = True
        for i in search_list:
            if region.find(i) == -1:
                flag = False
        if flag:
            tmp_dict[code] = region
    for i in tmp_dict.keys():
        hospitals_list = List().listHospitals(i)
        for j in hospitals_list:
            lpu_dict[j.uid.split('/')[0]] = j.name
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


def get_doctors_with_tickets(**kwargs):
    speciality = kwargs.get('speciality')
    data = list()
    _doctors = List().listDoctors(**kwargs)
    start = datetime.now(tzlocal()).astimezone(tz=timezone(_config('TIME_ZONE'))).replace(tzinfo=None)
    for doctor in getattr(_doctors, 'doctors', []):
        if speciality and doctor.speciality != speciality:
            continue
        hospital_uid = doctor.hospitalUid
        lpu_id, department_id = hospital_uid.split('/')
        _tickets = list()
        closest_tickets = Schedule().get_closest_tickets(hospital_uid, [doctor.uid], start=start)
        if closest_tickets:
            for key, value in enumerate(closest_tickets):
                _tickets.append(dict(href=url_for('.registration',
                                                  lpu_id=lpu_id,
                                                  department_id=department_id,
                                                  doctor_id=doctor.uid,
                                                  office=getattr(value, 'office', ''),
                                                  d=value['timeslotStart'].strftime('%Y%m%d'),
                                                  s=value['timeslotStart'].strftime('%H%M%S'),
                                                  f=value['timeslotEnd'].strftime('%H%M%S')),
                                     info=value['timeslotStart'].strftime('%d.%m %H:%M')))
        data.append(dict(uid=doctor.uid,
                         name=u' '.join([doctor.name.lastName, doctor.name.firstName, doctor.name.patronymic]),
                         schedule_href=url_for('.tickets',
                                               lpu_id=lpu_id,
                                               department_id=department_id,
                                               doctor_id=doctor.uid),
                         tickets=_tickets))
    return data


def prepare_doctors(doctors):
    data = list()
    for key, doctor in enumerate(getattr(doctors, 'doctors', [])):
        tmp = doctor.hospitalUid.split('/')
        lpu_id, department_id = tmp[0], tmp[1]
        data.append(dict(uid=doctor.uid,
                         name=u' '.join([doctor.name.lastName, doctor.name.firstName, doctor.name.patronymic]),
                         speciality=doctor.speciality,
                         hospitalUid=doctor.hospitalUid,
                         schedule_href=url_for('.tickets',
                                               lpu_id=lpu_id,
                                               department_id=department_id,
                                               doctor_id=doctor.uid),
                         hospital=dict(name=doctors.hospitals[key].name,
                                       address=doctors.hospitals[key].address)))
    return data