# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash, session, current_app

from jinja2 import TemplateNotFound
from wtforms import TextField, PasswordField, IntegerField
from flask_wtf import Form
from wtforms.validators import Required

from .app import module
from .lib.service_client import List, Info, Schedule


@module.route('/', methods=['GET'])
def index():
    return render_template('{0}/index.html'.format(module.name))


@module.route('/medical_institution/<okato>/', methods=['GET'])
def lpu(okato):
    return render_template('{0}/lpu.html'.format(module.name))


@module.route('/medical_institution/search/', methods=['GET'])
def search():
    return render_template('{0}/lpu.html'.format(module.name))


@module.route('/subdivisions/', methods=['GET'])
@module.route('/subdivisions/<lpu_id>/', methods=['GET'])
def departments(lpu_id=None):
    return render_template('department.html'.format(module.name))


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