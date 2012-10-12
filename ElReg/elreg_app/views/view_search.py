#coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from elreg_app.functions import InfoWSDL
import json

def index(request):
    """ Логика страницы search
    Страница создана только для динамической подгрузки данных при помощи AJAX'а.
    Вызывается на вкладке "ЛПУ".
    Запуск через адресную строку приведет к редиректу на главную страницу.
    """
    if request.method == 'GET':
        if request.GET.has_key('search'):
            hospitals_list = InfoWSDL().getHospitalInfo()

            # получение спика введенных пользователем слов
            search_list = request.GET.get( 'search' ).lower().split(' ')

            # формирование временного списка кортежей [(uid ЛПУ, наименование ЛПУ), ...]
            tmp_list = []
            for i in hospitals_list:
                tmp_list.append((i.uid.split('/')[0], i.title.lower()))

            # формирование словаря со значениями, удовлетворяющими поиску,
            # где ключ - uid ЛПУ, а значение - наименование ЛПУ
            lpu_dict ={}
            for (uid,title) in tmp_list:
                flag = True
                for i in search_list:
                    if title.find(i) == -1:
                        flag = False
                if flag:
                    lpu_dict[uid] = title

            # создание ответа в формате json:
            response = HttpResponse()
            response['Content_Type'] = "text/javascript"
            response.write(json.dumps(lpu_dict))
            return response
    else:
        return HttpResponseRedirect("/")
