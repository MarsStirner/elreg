# -*- coding: utf-8 -*-
DEBUG = True
# Конфигурация базы данных:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',         # Изменить окончание в зависимости от используемого СУБД:
                                                      # 'postgresql_psycopg2', 'mysql', 'sqlite3' или 'oracle'.
        'NAME': 'elreg',                              # Имя БД или путь до файла БД, если используется sqlite3.
        'USER': 'elreg_user',                         # Логин. Не используется с sqlite3.
        'PASSWORD': 'elreg_password',                 # Пароль. Не используется с sqlite3.
        'HOST': '',                                   # Оставить строку пустой, если используется на локальном
                                                      # хосте. Не используется с sqlite3.
        'PORT': '',                                   # Оставить строку пустой, если необходимо использовать номер
                                                      # порта по умолчанию. Не используется с sqlite3.
    }
}