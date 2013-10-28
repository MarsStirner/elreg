# -*- coding: utf-8 -*-
from datetime import datetime
from suds.client import Client
from suds.sax.text import Text
from config import DEBUG
from ..lib.utils import _config

IS = _config('IS_URL')


def unicode_result(value):
    # NOT USED yet
    if isinstance(value, basestring) or isinstance(value, Text):
        return unicode(value)
    if isinstance(value, list):
        for obj in value:
            return unicode_result(obj)
    if isinstance(value, list):
        for kk, vv in value.__dict__.iteritems():
            setattr(object, kk, unicode_result(vv))
    return value


class List():
    """ Класс для обращения к сервису list.wsdl.
    Класс содержит методы listHospitals и listDoctors, обращающиеся к одноименным методам web-сервиса.

    """
    def __init__(self):
        if DEBUG:
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


class Info():
    """ Класс для обращения к сервису info.wsdl.
    Класс содержит метод getHospitalInfo, обращающийся к одноименному методу web-сервиса.

    """
    def __init__(self):
        if DEBUG:
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


class Schedule():
    """ Класс для обращения к сервису schedule.wsdl.
    Класс содержит методы getScheduleInfo, getTicketStatus и enqueue, обращающиеся к одноименным методам web-сервиса.

    """
    def __init__(self):
        if DEBUG:
            self.client = Client(IS % "schedule", cache=None)
        else:
            self.client = Client(IS % "schedule")

    def getScheduleInfo(self, hospitalUid=0, doctorUid=0, startDate=None, endDate=None):
        """
        Метод возвращает расписания врачей.

        """
        try:
            params = {'hospitalUid': hospitalUid, 'doctorUid': doctorUid}
            if startDate and endDate:
                params.update(dict(startDate=startDate, endDate=endDate))
            ticket = self.client.service.getScheduleInfo(params).timeslots
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

    def get_closest_tickets(self, hospitalUid, doctors, start=None):
        """
        Метод возвращает информацию о ближайших талончиках.

        """
        if start is None:
            start = datetime.now()
        try:
            tickets = self.client.service.getClosestTickets({'hospitalUid': hospitalUid,
                                                            'doctors': doctors,
                                                            'start': start}).tickets
        except Exception, e:
            print e
            tickets = []
        return tickets