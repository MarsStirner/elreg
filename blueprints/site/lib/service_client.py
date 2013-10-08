# -*- coding: utf-8 -*-
from suds.client import Client

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
