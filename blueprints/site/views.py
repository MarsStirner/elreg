# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash, session, current_app, jsonify
import math

from jinja2 import TemplateNotFound
from wtforms import TextField, PasswordField, IntegerField
from flask_wtf import Form
from wtforms.validators import Required

from .app import module
from .lib.service_client import List, Info, Schedule
from .context_processors import header


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
    hospital_uid = '{0}/0'.format(lpu_id)
    lpu_info = None
    try:
        hospitals = Info().getHospitalInfo(hospitalUid=hospital_uid)
    except Exception, e:
        print e
    else:
        lpu_info = hospitals[0]
    return render_template('{0}/division.html'.format(module.name),
                           lpu_id=lpu_id,
                           lpu=lpu_info)


@module.route('/time/<int:doctor_id>/', methods=['GET'])
@module.route('/time/<int:doctor_id>/<start>/', methods=['GET'])
def tickets(doctor_id, start=None):
    session['step'] = 4
    return render_template('{0}/tickets.html'.format(module.name))


@module.route('/patient/', methods=['POST'])
def registration():
    session['step'] = 5
    return render_template('{0}/registration.html'.format(module.name))


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


@module.route('/ajax_doctors/<int:lpu_id>/<int:department_id>/<string:speciality>/', methods=['GET'])
def get_doctors(lpu_id=None, department_id=None, speciality=None):
    if not lpu_id or not department_id or not speciality:
        abort(404)
    data = list()
    doctors_list = List().listDoctors(hospital_Uid='{0}/{1}'.format(lpu_id, department_id),
                                      speciality=speciality)
    for doctor in doctors_list:
        if doctor.speciality == speciality:
            data.append(dict(uid=doctor.uid,
                             name=' '.join([doctor.name.lastName, doctor.name.firstName, doctor.name.patronymic]),
                             href=url_for('.tickets', doctor_id=doctor.uid)))
    return jsonify(result=data)