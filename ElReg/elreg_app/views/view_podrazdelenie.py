#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from suds.client import Client

def index(request, podrazd='00'):
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


    return render_to_response('podrazdelenie.html', {'podrazdelenie_list': podrazdelenie_list, 'current_lpu': current_lpu})