#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from lxml import etree

def index(request):
    tree = etree.parse("elreg_app/regions.xml")
    names, codes = [], []
    for i in tree.xpath('/regions/region/name'):
        names.append(i.text)
    for i in tree.xpath('/regions/region/code'):
        codes.append(i.text)
    names_codes = zip(names, codes)
    return render_to_response('index.html', {'names_codes': names_codes})