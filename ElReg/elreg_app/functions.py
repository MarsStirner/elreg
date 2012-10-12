# -*- coding: utf-8 -*-

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from ElReg.settings import IS
from suds.client import Client


class ListWSDL():
    wsdl = "list"
    def listHospitals(self, okato=0):
        try:
            if okato:
                hospitals = Client(IS + self.wsdl).service.listHospitals(ocatoCode=okato).hospitals
            else:
                hospitals = Client(IS + self.wsdl).service.listHospitals().hospitals
        except:
            hospitals = []
        return hospitals

    def listDoctors(self):
        try:
            doctors = Client(IS + self.wsdl).service.listDoctors().doctors
        except:
            doctors = []
        return doctors


class InfoWSDL():
    wsdl = "info"
    def getHospitalInfo(self):
        try:
            info_list = Client(IS + self.wsdl).service.getHospitalInfo()
        except:
            info_list = []
        return info_list


class ScheduleWSDL():
    wsdl = "schedule"
    def getScheduleInfo(self, hospitalUid=0, doctorUid=0):
        try:
            ticket = Client(IS + self.wsdl).service.getScheduleInfo(hospitalUid=hospitalUid, doctorUid=doctorUid)
        except:
            ticket = []
        return ticket

    def getTicketStatus(self, hospitalUid=0, ticketUid=0):
        try:
            ticket = Client(IS + self.wsdl).service.getTicketStatus(hospitalUid=hospitalUid, ticketUid=ticketUid)[0]
        except:
            ticket = []
        return ticket

    def enqueue(self, person=0, omiPolicyNumber=0, hospitalUid=0, doctorUid=0, timeslotStart=0, hospitalUidFrom=0, birthday=0):
        try:
            ticket = Client(IS + self.wsdl).service.enqueue(person, omiPolicyNumber, hospitalUid, doctorUid, timeslotStart, hospitalUidFrom, birthday)
        except:
            ticket = []
        return ticket


def stringValidation(s):
  w = []
  s = r'%s' % s
  w.append(s.find('<'))
  w.append(s.find('>'))
  w.append(s.find('\\'))
  w.append(s.find('script'))
  w.append(s.find('SELECT'))
  w.append(s.find('UPDATE'))
  w.append(s.find('ALTER'))
  w.append(s.find('DROP'))
  try:
    for i in list(xrange(6)):
      if w[i] == -1:
        continue
      else:
        raise SyntaxError
    return s
  except (ValueError, SyntaxError, TypeError):
    return 0

def emailValidation(value):
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False
