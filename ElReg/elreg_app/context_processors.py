# -*- coding: utf-8 -*-

from elreg_app.functions import Redis

def globalContext(request):
    db = Redis(request)

    return {
        'step': db.get('step'),                             # номер шага (вкладки на сайте)
        'current_lpu_title': db.get('current_lpu_title'),   # наименование выбранного ЛПУ
        'current_lpu_phone': db.get('current_lpu_phone'),   # номер телефона выбранного ЛПУ
        'address': db.get('address'),                       # адрес выбранного ЛПУ
        'speciality': db.get('speciality'),                 # специальность выбранного врача
        'doctor': db.get('doctor'),                         # ФИО выбранного врача
    }
