#coding: utf-8

from ElReg.settings import redis_db

def customProc(request):
    id = request.session.session_key
    step = int(redis_db.hget(id, 'step'))
    prof = redis_db.hget(id, 'prof')
    date = redis_db.hget(id, 'date')
    current_podrazd = redis_db.hget(id, 'current_podrazd')
    docName = redis_db.hget(id, 'docName')

    return locals()