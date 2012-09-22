#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from suds.client import Client

def index(request, template_name, podrazd='00'):
    base_url = "http://10.1.2.107/int-server/index.php?wsdl=info"
    client = Client(base_url)
    try:
        x = client.service.getHospitalInfo()
    except:
        x = ''
    podrazdelenie_list = []
    for c in x:
        if c.uid.startswith('%s'%(podrazd)):
            current_lpu = c
            for b in c.buildings:
                podrazdelenie_list.append(b.title)

    new_list = []
    base_url = "http://10.1.2.107/int-server/index.php?wsdl=list"
    client = Client(base_url)
    y = client.service.listHospitals().hospitals
    for v in y:
        for w in podrazdelenie_list:
            if v.uid.startswith('%s'%(podrazd)) and v.title == w:
                new_list.append(v.uid)
    new = zip(podrazdelenie_list, new_list)
    return render_to_response(template_name, {'podrazdelenie_list': podrazdelenie_list, 'current_lpu': current_lpu, 'new_list': new_list, 'new': new})