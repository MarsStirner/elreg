#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from ElReg.settings import redis_db, client_list, client_schedule
import datetime
import calendar
import time

def index(request, template_name, vremya='00'):
    """
    Логика страницы Время
    """
    try:
        hospital_Uid = redis_db.get('hospital_Uid')
        vr = client_schedule.service.getScheduleInfo(hospitalUid=hospital_Uid, doctorUid=vremya)
        vr0 = []
        for v in vr:
            vr0.append((v.start.date(), v))
        vr = vr0
    except:
        vr = ''
    current_podrazd = redis_db.get('current_podrazd')
    prof = redis_db.get('prof')
    docName = ''
    for i in client_list.service.listDoctors().doctors:
        if i.uid == vremya:
            docName = i.name
            redis_db.set('docName', docName)
    week = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
    weeks = [0,1,2,3,4,5,6]


    now = datetime.date.today()
    x = datetime.date.isoweekday(now)
    td1 = datetime.timedelta(days=x-1)
    td2 = datetime.timedelta(days=7-x)
    res1 = now - td1
    res2 = now + td2
#    res1 = res1 + datetime.timedelta(days=2)

    times = []
    dates = []

    for i in xrange(7):
        newDay = res1 + datetime.timedelta(days=i)
        dates.append(newDay)
        for m in vr:
            if newDay == m[1].start.date():
                times.append((m[1].start.time(), m[1].finish.time()))
    times = list(set(times))
    times.sort()



    superList = []
#    newSuperList = []
    for time in times:
        for date in dates:
                for v in vr:
                    if v[1].start.time() == time[0] and v[1].start.date() == date:
                        superList.append(v[1].status)



#    for v in xrange(0, len(superList), 7):
#        newSuperList.append([superList[v+i] for i in xrange(7)])

#            for v in xrange(0, len(vr), 7):
#                superList = []
#                for w in xrange(7):
#                    if vr[v+w].start.time() == time and vr[v+w].start.date() == date:
#                        superList.append(vr[v+w].status)
#                    else:
#                        superList.append('0')
#                newSuperList.append(superList)

#    for v in xrange(0, len(superList), 7):
#        newSuperList.append([superList[v+i] for i in xrange(7)])




    redis_db.set('step', 6)
    return render_to_response(template_name, {'vr': vr,
                                              'current_podrazd': current_podrazd,
                                              'prof': prof,
                                              'docName': docName,
                                              'week': week,
                                              'weeks': weeks,
                                              'times': times,
                                              'dates': dates,
                                              'superList': superList,
#                                              'newSuperList': newSuperList,
                                              'step': redis_db.get('step')})
