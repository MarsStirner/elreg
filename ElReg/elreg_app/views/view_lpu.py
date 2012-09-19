#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from suds.client import Client

def index(request, okato):
    base_url = "http://10.1.2.107/int-server/index.php?wsdl=list"
    client = Client(base_url)
    info = client.service.listHospitals(ocatoCode=okato)
    return render_to_response('lpu.html', {'lpu': info[0][0][1]})