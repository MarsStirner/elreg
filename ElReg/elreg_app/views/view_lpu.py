#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from suds.client import Client
from lxml import etree

def index(request, okato='0000000000'):
    base_url = "http://10.1.2.107/int-server/index.php?wsdl=list"
    client = Client(base_url)
    try:
        hospitals_list = client.service.listHospitals(ocatoCode=okato).hospitals
    except:
        hospitals_list = ''
    tree = etree.parse("elreg_app/regions.xml")
    names, codes = [], []
    for i in tree.xpath('/regions/region/name'):
        names.append(i.text)
    for i in tree.xpath('/regions/region/code'):
        codes.append(i.text)
    x = names[codes.index(okato)]
    return render_to_response('lpu.html', {'hospitals_list': hospitals_list, 'x': x})