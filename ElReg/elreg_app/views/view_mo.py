#coding: utf-8

from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import render_to_response
from elreg_app.models import Region
from ElReg.settings import redis_db

def index(request, template_name):
    """ Логика страницы МО
    Главная страница сайта. На ней происходит проверка на наличие у пользователя идентификатора сессии
    и создание сессии пользователя в случае отсутствия идентификатора. А также происходит получение
    списка доступных регионов, установленных в административном интерфейсе.
    """

    # проверка на наличие идентификатора сессии:
    id = request.session.session_key
    if not id:
        s = SessionStore()
        s.save()
        id = s.session_key
    redis_db.hset(id, 'step', 1)

    # получение списка регионов:
    region_list = Region.objects.filter(activation=True)
    return render_to_response(template_name, {'region_list': region_list,
                                              'step': int(redis_db.hget(id, 'step'))})
