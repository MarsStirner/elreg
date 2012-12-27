# -*- coding: utf-8 -*-

import os

# адрес интеграционного сервера
IS = "http://127.0.0.1:9910/%s/?wsdl"

DEBUG = True

DEBUG_SECURE = DEBUG

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

# Полный путь до директории проекта
PROJECT_ROOT = (os.path.dirname(__file__) + '/').replace('\\', '/')

# Имя приложения
APP_NAME = 'elreg_app'

# Полный путь до директории приложения
APP_ROOT = os.path.join(PROJECT_ROOT, APP_NAME + '/')

MANAGERS = ADMINS

# Конфигурация базы данных:
DATABASES = {
    'default': {
        'ENGINE': '',         # Изменить окончание в зависимости от используемого СУБД:
                                                        # 'postgresql_psycopg2', 'mysql', 'sqlite3' или 'oracle'.
        'NAME': '', # Имя БД или путь до файла БД, если используется sqlite3.
        'USER': '',                                     # Логин. Не используется с sqlite3.
        'PASSWORD': '',                                 # Пароль. Не используется с sqlite3.
        'HOST': '',                                     # Оставить строку пустой, если используется на локальном
                                                        # хосте. Не используется с sqlite3.
        'PORT': '',                                     # Оставить строку пустой, если необходимо использовать номер
                                                        # порта по умолчанию. Не используется с sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'

LANGUAGES = (
    ('ru', 'Russian'),
    ('en', 'English'),
    )

SITE_ID = 1

APPEND_SLASH = True

ROOT_URL = '/'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(APP_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ROOT_URL + 'media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(APP_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = ROOT_URL + 'static_admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ru6*p_@g(kke)y25$1a*36v!m%&amp;j)6!qth27b10fmwb=+v$g%_'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
#    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.csrf',
    'elreg_app.context_processors.globalContext',
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(APP_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    APP_NAME,
    'livesettings',
    'custom_livesettings',
    'captcha',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SESSION_COOKIE_HTTPONLY = True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CACHE_PREFIX = 'elreg'
CACHE_TIMEOUT = 300

# Конфигурация CAPTCHA
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = ()
CAPTCHA_LETTER_ROTATION = (-10, 10)
CAPTCHA_FOREGROUND_COLOR = '#000'

# Конфигурация электронной почты:

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

#EMAIL_HOST = 'localhost'                # адрес smtp-сервера. например 'smtp.gmail.com'
#                                        # для локального хоста - 'localhost'
#EMAIL_PORT = 1025                       # порт smtp-сервера (обычно 587 или 25 для TLS или 465 для SSL)
#                                        # для локального хоста - обычно порт 1025
#EMAIL_HOST_USER = ''                    # логин
#EMAIL_HOST_PASSWORD = ''                # пароль
#EMAIL_USE_TLS = False                   # включить/отключить TLS (для тестового режима - False)
#DEFAULT_FROM_EMAIL = 'no-reply@elreg.ru'

# Импортируем настройки из локального конфига
from settings_local import *