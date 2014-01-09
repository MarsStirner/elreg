# -*- coding: utf-8 -*-
from flask import copy_current_request_context
from datetime import datetime, timedelta, date
import hashlib
from threading import Thread
from random import randint
from pytz import timezone
from dateutil.tz import tzlocal
from flask import url_for, session
from jinja2 import Environment, PackageLoader
from service_client import List, Info, Schedule
from application.app import db
from application.models import Tickets, TicketsBlocked
from ..app import module
from utils import _config, logger, datetime_now
from ..config import BLOCK_TICKET_TIME


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


def save_ticket(ticket_uid, lpu_id, department_id, doctor_id, lpu_info):
    import hashlib
    uid = hashlib.md5('{0}/{1}/{2}/{3}'.format(lpu_id, department_id, doctor_id, ticket_uid)).hexdigest()
    env = Environment(loader=PackageLoader(module.import_name,  module.template_folder))
    template = env.get_template('{0}/_ticket.html'.format(module.name))
    info = template.render(lpu=lpu_info, session=session)
    ticket = Tickets(uid=uid, ticket_uid=ticket_uid, info=info, created=datetime_now())
    db.session.add(ticket)
    db.session.commit()
    return uid


def find_lpu(region_list, search_input, result):
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


def gen_blocked_ticket_uid(lpu_id, department_id, doctor_id, timeslot, time_index=None):
    return unicode(hashlib.md5(u'{0}{1}{2}{3}'.format(lpu_id, department_id, doctor_id, str(timeslot))).hexdigest())


def block_ticket(lpu_id, department_id, doctor_id, timeslot, date, start, end, time_index=None):
    ticket_uid = gen_blocked_ticket_uid(lpu_id, department_id, doctor_id, timeslot, time_index=None)
    ticket = TicketsBlocked(lpu_id=lpu_id,
                            department_id=department_id,
                            doctor_id=doctor_id,
                            d=date,
                            s=start,
                            f=end,
                            timeslot=timeslot,
                            timeIndex=time_index,
                            ticket_uid=ticket_uid[0:40],
                            created=datetime_now(),
                            status='blocked')
    db.session.add(ticket)
    db.session.commit()
    block_until = datetime_now() + timedelta(seconds=BLOCK_TICKET_TIME)
    return dict(block_until=block_until, ticket_uid=ticket_uid)


def get_blocked_tickets(lpu_id, department_id, doctor_id):
    tickets = dict()
    block_diff_datetime = datetime_now() - timedelta(seconds=BLOCK_TICKET_TIME)
    result = db.session.query(TicketsBlocked).filter(TicketsBlocked.lpu_id == lpu_id,
                                                     TicketsBlocked.department_id == department_id,
                                                     TicketsBlocked.doctor_id == doctor_id,
                                                     TicketsBlocked.status == 'blocked',
                                                     TicketsBlocked.created > block_diff_datetime)
    for row in result.all():
        tickets[row.timeslot] = dict(ticket_uid=row.ticket_uid,
                                     block_until=row.created + timedelta(seconds=BLOCK_TICKET_TIME))
    return tickets


def check_blocked_ticket(lpu_id, department_id, doctor_id, timeslot):
    block_diff_datetime = datetime_now() - timedelta(seconds=BLOCK_TICKET_TIME)
    ticket = (db.session.query(TicketsBlocked)
              .filter(TicketsBlocked.lpu_id == lpu_id,
                      TicketsBlocked.department_id == department_id,
                      TicketsBlocked.doctor_id == doctor_id,
                      TicketsBlocked.timeslot == timeslot,
                      TicketsBlocked.created > block_diff_datetime)
              .order_by(TicketsBlocked.created.desc())
              .first())
    return ticket


def get_blocked_ticket_by_uid(ticket_uid):
    block_diff_datetime = datetime_now() - timedelta(seconds=BLOCK_TICKET_TIME)
    ticket = (db.session.query(TicketsBlocked)
              .filter(TicketsBlocked.ticket_uid == ticket_uid)
              .order_by(TicketsBlocked.created.desc())
              .first())
    if ticket.status == 'blocked':
        if ticket.created < block_diff_datetime:
            ticket.status = 'free'
            change_ticket_status(ticket.ticket_uid, 'free')
        if ticket.timeslot < datetime_now():
            ticket.status = 'disabled'
            change_ticket_status(ticket.ticket_uid, 'disabled')
    return ticket


def delete_blocked_ticket(ticket_uid):
    db.session.query(TicketsBlocked).filter(TicketsBlocked.ticket_uid == ticket_uid).delete()
    db.session.commit()


def change_ticket_status(ticket_uid, status='free'):
    try:
        updated = datetime_now()
        result = (db.session.query(TicketsBlocked)
                  .filter(TicketsBlocked.ticket_uid == ticket_uid)
                  .update({'status': status, 'updated': updated}))
        db.session.commit()
    except Exception, e:
        print e


def async_clear_blocked_tickets():
    @copy_current_request_context
    def clear_blocked_tickets():
        try:
            clear_date = datetime_now() + timedelta(days=100)
            db.session.query(TicketsBlocked).filter(TicketsBlocked.created > clear_date).delete()
        except Exception, e:
            print e
            return False
        return True

    thr = Thread(target=clear_blocked_tickets)
    thr.start()


def find_ticket(ticket_uid, lpu_id, department_id, doctor_id):
    return db.session.query(Tickets).filter(
        Tickets.ticket_uid==ticket_uid,
        lpu_id==lpu_id,
        department_id==department_id,
        doctor_id==doctor_id).first()