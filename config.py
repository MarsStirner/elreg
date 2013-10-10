# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

DB_DRIVER = 'mysql'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'elreg_login'
DB_PASSWORD = 'elreg_password'
DB_NAME = 'elreg'
DB_CONNECT_OPTIONS = ''

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8800

SYSTEM_USER = 'elreg'

CSRF_ENABLED = True
SECRET_KEY = ''


try:
    from config_local import *
except ImportError:
    # no local config found
    pass

SQLALCHEMY_DATABASE_URI = '{0}://{1}:{2}@{3}:{4}/{5}{6}'.format(DB_DRIVER,
                                                       DB_USER,
                                                       DB_PASSWORD,
                                                       DB_HOST,
                                                       DB_PORT,
                                                       DB_NAME,
                                                       DB_CONNECT_OPTIONS)