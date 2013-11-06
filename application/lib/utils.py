# -*- coding: utf-8 -*-
from flask import g, current_app
from flask.ext.principal import identity_loaded, Principal, Permission, RoleNeed, UserNeed
from flask.ext.login import LoginManager, current_user
from application.app import app
from ..database import db
from ..models import Settings, Users, Roles


def public_endpoint(function):
    function.is_public = True
    return function


def create_config_func(module_name=None, config_table=None):

    def _config(code):
        """Возвращает значение конфигурационной переменной, полученной из таблицы %config_table%"""
        #Get app_settings
        app_settings = dict()
        config = dict()
        with app.app_context():
            try:
                for item in db.session.query(Settings).all():
                    app_settings.update({item.code: item.value})
                # app_settings = {item.code: item.value for item in db.session.query(Settings).all()}
            except Exception, e:
                print e

        if module_name:
            config = getattr(g, '%s_config' % module_name, None)
        if not config and config_table is not None:
            values = db.session.query(config_table).all()
            config = dict()
            for value in values:
                config[value.code] = value.value
            setattr(g, '%s_config' % module_name, config)

        config.update(app_settings)
        return config.get(code, None)

    return _config


with app.app_context():
    permissions = dict()
    login_manager = LoginManager()
    try:
        roles = db.session.query(Roles).all()
    except Exception, e:
        print e
        permissions['admin'] = Permission(RoleNeed('admin'))
    else:
        if roles:
            for role in roles:
                permissions[role.code] = Permission(RoleNeed(role.code))
                permissions[role.code].description = role.description
        else:
            permissions['admin'] = Permission(RoleNeed('admin'))

admin_permission = permissions.get('admin')
user_permission = permissions.get('user')


def stringValidation(string):
    """
    Простой валидатор переменных типа str, который проверяет наличие в строке SQL-команд.

    """
    string = r'%s' % string
    for i in ['<', '>', '\\', 'script', 'SELECT', 'UPDATE', 'ALTER', 'DROP']:
        if string.find(i) != -1:
            return False
    return True