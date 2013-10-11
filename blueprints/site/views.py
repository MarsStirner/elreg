# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash, session, current_app
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
    if okato != "search":
        hospitals_list = List().listHospitals(okato)  # список ЛПУ выбранного региона
        for hospital in hospitals_list:
            hospital.uid = hospital.uid.split('/')[0]
    return render_template('{0}/lpu.html'.format(module.name), hospitals_list=hospitals_list)

@module.route('/medical_institution/search/', methods=['GET'])
def search():
    return render_template('{0}/lpu.html'.format(module.name))


@module.route('/division/', methods=['GET'])
@module.route('/division/<lpu_id>/', methods=['GET'])
def division(lpu_id=None):
    """Логика страницы Подразделение/Специализация/Врач
    Выводится список подразделений для выбранного ЛПУ. Остальная логика
    """

    hospitalUid = 0
    try:
        hospitalUid = lpu_id.split('/')[0] + '/0'
    except:
        pass

    tmp1_list, subdivision_list = [], []
    current_lpu = None

    try:
        if hospitalUid:
            hospital = Info().getHospitalInfo(hospitalUid=hospitalUid)
        else:
            hospital = Info().getHospitalInfo()

        for i in hospital:
            if i.uid.startswith(lpu_id):
                current_lpu = i
                for j in i.buildings:
                    subdivision_list.append({
                        'name': unicode(j.name),
                        'id': j.id,
                        'address': unicode(j.address) if j.address else ""
                    })
    except:
        pass

    return render_template('{0}/division.html'.format(module.name), lpu_id=lpu_id, current_lpu=current_lpu,
                           subdivision_list=subdivision_list)


@module.route('/time/<int:doctor_id>/', methods=['GET'])
@module.route('/time/<int:doctor_id>/<start>/', methods=['GET'])
def tickets(doctor_id, start=None):
    return render_template('{0}/tickets.html'.format(module.name))


@module.route('/patient/', methods=['POST'])
def registration():
    return render_template('{0}/registration.html'.format(module.name))


@module.route('/register/', methods=['POST'])
def ticket_info():
    return render_template('{0}/ticket_info.html'.format(module.name))