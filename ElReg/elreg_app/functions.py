# -*- coding: utf-8 -*-

from django.contrib.sessions.backends.db import SessionStore
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import config
from livesettings import config_value
from suds.client import Client
import redis
import settings

import logging
if settings.DEBUG:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.CRITICAL)
else:
    logging.basicConfig(level=logging.CRITICAL)
    logging.getLogger('suds.client').setLevel(logging.CRITICAL)


IS = config_value('IS', 'URL')

class Redis ():
    """ Класс для обращения к серверу redis.
    Класс содержит методы, котрые сохраняют единственный элемент (принимает ключ:значение) или множество
    элементов (принимает словарь), а также получают данные из базы redis на основании полученного идентификатора
    сессии и пары ключ:значение.

    """
    # конфигурация сервера redis:
    db = redis.StrictRedis(host='localhost', port=6379, db=0)

    def __init__(self, request):
        self.id = self.sessionId(request)

    def set(self, key, value=False):
        """
        Запись в базу идентификатора сессии, ключа и значения для единственного полученного элемента (key, value),
        либо для каждого элемента полученного словаря (key=словарь, value=False).

        """
        if value:
            self.db.hset(self.id, key, value)
        elif isinstance(key, dict):
            for (key, value) in key.items():
                self.set(key, value)
        else:
            self.db.hset(self.id, key, "")
            self.delete([key])

    def delete(self, *names):
        self.db.delete(*names)

    def get(self, key):
        """
        Получение значения из базы по идентификатору сессии и ключу. Возвращается значение типа string во всех
        случаях, кроме случая, когда ключ равен "step" - тогда возвращается значение типа integer.

        """
        result = self.db.hget(self.id, key)
        if key == "step":
            try:
                result = int(result)
            except TypeError:
                result = ''
        return result

    def sessionId(self, request):
        """
        Получение идентификатора сессии или, в случае его отсутствия, создание идентификатора сессии.

        """
        id = request.session.get('session_id', False)
        if not id:
            s = SessionStore()
            s.save()
            id = s.session_key
        request.session['session_id'] = id
        return id


class ListWSDL():
    """ Класс для обращения к файлу list.wsdl.
    Класс содержит методы listHospitals и listDoctors, обращающиеся к одноименным методам web-сервиса.

    """
    def __init__(self):
        if settings.DEBUG:
            self.client = Client(IS % "list", cache=None)
        else:
            self.client = Client(IS % "list")

    def listRegions(self):
        """Получение списка регионов из ИС"""
        try:
            regions = self.client.service.listRegions().regions
        except Exception, e:
            print e
            regions = []
        return regions

    def listHospitals(self, okato=0):
        """
        Метод принимает код ОКАТО и возвращает ЛПУ, удовлетворяющее требованию, или список ЛПУ,
        в случае, если код ОКАТО указан не был.

        """
        try:
            if okato:
                hospitals = self.client.service.listHospitals({'ocatoCode': okato}).hospitals
            else:
                hospitals = self.client.service.listHospitals().hospitals
        except Exception, e:
            print e
            hospitals = []
        return hospitals

    def listDoctors(self, hospital_Uid = 0, speciality = 0):
        """
        Метод возвращает список врачей.

        """
        try:
            if hospital_Uid:
                if speciality:
                    doctors = self.client.service.listDoctors({
                        'searchScope': {'hospitalUid': hospital_Uid, }, 'speciality': speciality
                    }).doctors
                else:
                    doctors = self.client.service.listDoctors({'searchScope': {'hospitalUid': hospital_Uid, }}).doctors
            else:
                doctors = self.client.service.listDoctors().doctors
        except Exception, e:
            print e
            doctors = []
        return doctors


class InfoWSDL():
    """ Класс для обращения к файлу info.wsdl.
    Класс содержит метод getHospitalInfo, обращающийся к одноименному методу web-сервиса.

    """
    def __init__(self):
        if settings.DEBUG:
            self.client = Client(IS % "info", cache=None)
        else:
            self.client = Client(IS % "info")

    def getHospitalInfo(self, hospitalUid=0):
        """
        Метод возвращает инвормацию об ЛПУ.

        """
        try:
            if hospitalUid:
                info_list = self.client.service.getHospitalInfo({'hospitalUid': hospitalUid}).info
            else:
                info_list = self.client.service.getHospitalInfo().info
        except Exception, e:
            print e
            info_list = []
        return info_list


class ScheduleWSDL():
    """ Класс для обращения к файлу schedule.wsdl.
    Класс содержит методы getScheduleInfo, getTicketStatus и enqueue, обращающиеся к одноименным методам web-сервиса.

    """
    def __init__(self):
        if settings.DEBUG:
            self.client = Client(IS % "schedule", cache=None)
        else:
            self.client = Client(IS % "schedule")

    def getScheduleInfo(self, hospitalUid=0, doctorUid=0):
        """
        Метод возвращает расписания врачей.

        """
        try:
            ticket = self.client.service.getScheduleInfo({'hospitalUid': hospitalUid, 'doctorUid': doctorUid}).timeslots
        except Exception, e:
            print e
            ticket = []
        return ticket

    def getTicketStatus(self, hospitalUid=0, ticketUid=0):
        """
        Метод возвращает информацию о записи на приём. Не используется.

        """
        try:
            ticket = self.client.service.getTicketStatus({'hospitalUid': hospitalUid, 'ticketUid': ticketUid})
        except Exception, e:
            print e
            ticket = []
        return ticket

    def enqueue(self, person, document, hospitalUid, doctorUid, timeslotStart, hospitalUidFrom, birthday, sex):
        """
        Метод принимает данные о пациенте и возвращает номер талона и результат записи на приём.

        """
        try:
            ticket = self.client.service.enqueue({
                'person': person,
                'document': document,
                'hospitalUid': hospitalUid,
                'doctorUid': doctorUid,
                'timeslotStart': timeslotStart,
                'hospitalUidFrom': hospitalUidFrom,
                'birthday': birthday,
                'sex': sex
            })
        except Exception, e:
            print e
            ticket = []
        return ticket


def stringValidation(string):
    """
    Простой валидатор переменных типа str, который проверяет наличие в строке SQL-команд.

    """
    string = r'%s' % string
    for i in ['<', '>', '\\', 'script', 'SELECT', 'UPDATE', 'ALTER', 'DROP']:
        if string.find(i) != -1:
            return False
    return True


def emailValidation(value):
    """
    Простой валидатор адреса электронной почты, который сопоставляет введенный адрес с регулярным выражением.

    """
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False
