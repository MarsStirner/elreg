#coding: utf-8

from django.shortcuts import render_to_response
from ElReg.settings import redis_db, client
import datetime

def index(request, template_name, vremya=0):
    """
    Логика страницы Время
    """
    id = '%s' % request.session.session_key
    if not vremya or vremya in ['next','prev']:
        if not vremya:
            now = datetime.date.today()
            firstweekday = now - datetime.timedelta(days=datetime.date.isoweekday(now)-1)
        elif vremya == 'next':
            a = redis_db.hget(id, 'firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) + datetime.timedelta(days=7)
        elif vremya == 'prev':
            a = redis_db.hget(id, 'firstweekday').split('-')
            firstweekday = datetime.date(int(a[0]), int(a[1]), int(a[2])) - datetime.timedelta(days=7)
        vremya = redis_db.hget(id, 'vremya')
    else:
        now = datetime.date.today()
        firstweekday = now - datetime.timedelta(days=datetime.date.isoweekday(now)-1)
    try:
        hospital_Uid = redis_db.hget(id, 'hospital_Uid')
        ticketList = client("schedule").service.getScheduleInfo(hospitalUid=hospital_Uid, doctorUid=vremya)
    except:
        ticketList = []

    docName = '' # ФИО врача
    for i in client("list").service.listDoctors().doctors:
        if i.uid == vremya:
            docName = i.name
            docName = '%s %s %s' % (docName.lastName, docName.firstName, docName.patronymic)
            redis_db.hset(id, 'docName', docName)

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

    redis_db.hset(id, 'vremya', vremya)
    redis_db.hset(id, 'firstweekday', firstweekday)
    redis_db.hset(id, 'step', 6)
    return render_to_response(template_name, {'current_podrazd': redis_db.hget(id, 'current_podrazd'),
                                              'prof': redis_db.hget(id, 'prof'),
                                              'docName': docName,
                                              'dates': dates,
                                              'times': times,
                                              'ticketTable': ticketTable,
                                              'step': int(redis_db.hget(id, 'step'))})
