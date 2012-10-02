#coding: utf-8

from django.shortcuts import render_to_response
from ElReg.settings import redis_db, client
import datetime

def index(request, template_name, vremya='0'):
    """
    Логика страницы Время
    """
    if vremya in ['0','next','prev']:
        if vremya == 'next':
            a = redis_db.get('firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) + datetime.timedelta(days=7)
        elif vremya == 'prev':
            a = redis_db.get('firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) - datetime.timedelta(days=7)
        elif vremya == '0':
            now = datetime.date.today()
            firstweekday = now - datetime.timedelta(days=datetime.date.isoweekday(now)-1)
        vremya = redis_db.get('vremya')
    else:
        now = datetime.date.today()
        firstweekday = now - datetime.timedelta(days=datetime.date.isoweekday(now)-1)
    try:
        hospital_Uid = redis_db.get('hospital_Uid')
        ticketList = client("schedule").service.getScheduleInfo(hospitalUid=hospital_Uid, doctorUid=vremya)
    except:
        ticketList = []

    docName = '' # ФИО врача
    for i in client("list").service.listDoctors().doctors:
        if i.uid == vremya:
            docName = i.name
            docName = '%s %s %s' % (docName.lastName, docName.firstName, docName.patronymic)
            redis_db.set('docName', docName)

    times = [] # Список времен начала записи текущей недели
    dates = [] # Список дат текущей недели

    for i in xrange(7):
        newDay = firstweekday + datetime.timedelta(days=i)
        dates.append(newDay)
        for ticket in ticketList:
            if newDay == ticket.start.date():
                times.append(ticket.start.time())
        times = list(set(times))
        times.sort()

    if not times:
        ticketTable = []
    else:
        currentTicketList = []
        for ticket in ticketList:
            if ticket.start.date() in dates:
                currentTicketList.append(ticket)

        ticketTable = []
        for time in times:
            tmpList = [0]*7
            for ticket in currentTicketList:
                if ticket.start.time() == time:
                    tmpList[dates.index(ticket.start.date())] = ticket
            ticketTable.append(tmpList)

    redis_db.set('vremya', vremya)
    redis_db.set('firstweekday', firstweekday)
    redis_db.set('step', 6)
    return render_to_response(template_name, {'current_podrazd': redis_db.get('current_podrazd'),
                                              'prof': redis_db.get('prof'),
                                              'docName': docName,
                                              'dates': dates,
                                              'times': times,
                                              'ticketTable': ticketTable,
                                              'step': int(redis_db.get('step'))})
