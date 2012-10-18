# -*- coding: utf-8 -*-

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from settings import IS
from suds.client import Client


import redis
from django.contrib.sessions.backends.db import SessionStore
#redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

class RedisDB ():
    redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)
    def __init__(self, request):
        self.id = request.session.session_key
        if not self.id:
            s = SessionStore()
            s.save()
            self.id = s.session_key

    def set(self, key, value):
        self.redis_db.hset(self.id, key, value)

    def get(self, key):
        result = self.redis_db.hget(self.id, key)
        if key == "step":
            result = int(result)
        return result









class ListWSDL():
    """ Класс для обращения к файлу list.wsdl.
    Класс содержит методы listHospitals и listDoctors, обращающиеся к одноименным методам web-сервиса.

    """
    client = Client(IS + "list")
    def listHospitals(self, okato=0):
        """
        Метод принимает код ОКАТО и возвращает ЛПУ, удовлетворяющее требованию, или список ЛПУ,
        в случае, если код ОКАТО указан не был.

        """
        try:
            if okato:
                hospitals = self.client.service.listHospitals(ocatoCode=okato).hospitals
            else:
                hospitals = self.client.service.listHospitals().hospitals
        except:
            hospitals = []
        return hospitals

    def listDoctors(self):
        """
        Метод возвращает список врачей.

        """
        try:
            doctors = self.client.service.listDoctors().doctors
        except:
            doctors = []
        return doctors


class InfoWSDL():
    """ Класс для обращения к файлу info.wsdl.
    Класс содержит метод getHospitalInfo, обращающийся к одноименному методу web-сервиса.

    """
    client = Client(IS + "info")
    def getHospitalInfo(self):
        """
        Метод возвращает инвормацию об ЛПУ.

        """
        try:
            info_list = self.client.service.getHospitalInfo()
        except:
            info_list = []
        return info_list


class ScheduleWSDL():
    """ Класс для обращения к файлу schedule.wsdl.
    Класс содержит методы getScheduleInfo, getTicketStatus и enqueue, обращающиеся к одноименным методам web-сервиса.

    """
    client = Client(IS + "schedule")
    def getScheduleInfo(self, hospitalUid=0, doctorUid=0):
        """
        Метод возвращает расписания врачей.

        """
        try:
            ticket = self.client.service.getScheduleInfo(hospitalUid=hospitalUid, doctorUid=doctorUid)
        except:
            ticket = []
        return ticket

    def getTicketStatus(self, hospitalUid=0, ticketUid=0):
        """
        Метод возвращает информацию о записи на приём.

        """
        try:
            ticket = self.client.service.getTicketStatus(hospitalUid=hospitalUid, ticketUid=ticketUid)[0]
        except:
            ticket = []
        return ticket

    def enqueue(self, person, omiPolicyNumber, hospitalUid, doctorUid, timeslotStart, hospitalUidFrom, birthday):
        """
        Метод принимает данные о пациенте и возвращает номер талона и результат записи на приём.

        """
        try:
            ticket = self.client.service.enqueue(person=person, omiPolicyNumber=omiPolicyNumber, hospitalUid=hospitalUid, doctorUid=doctorUid, timeslotStart=timeslotStart, hospitalUidFrom=hospitalUidFrom, birthday=birthday)
        except:
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
