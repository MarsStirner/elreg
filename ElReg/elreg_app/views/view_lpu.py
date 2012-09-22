#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from suds.client import Client
from elreg_app.models import Region


def index(request, template_name, okato='0'):
    hospitals_list = []
    if okato == '0':
        base_url = "http://10.1.2.107/int-server/index.php?wsdl=info"
        client = Client(base_url)
        info = client.service.getHospitalInfo()
        for x in range(len(info)):
            hospitals_list.append(info[x])
    else:
        base_url = "http://10.1.2.107/int-server/index.php?wsdl=list"
        client = Client(base_url)
        try:
            hospitals_list = client.service.listHospitals(ocatoCode=okato).hospitals
        except:
            hospitals_list = ''
    current_region = '' if okato == '0' else Region.objects.get(code=okato)
    region_list = Region.objects.filter(activation=True)
    return render_to_response(template_name, {'hospitals_list': hospitals_list, 'region_list': region_list, 'current_region': current_region})