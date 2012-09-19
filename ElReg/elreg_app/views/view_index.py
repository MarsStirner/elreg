#!/usr/bin/env python
#coding: utf-8

from django.shortcuts import render_to_response
from lxml import etree

def index(request):
    tree = etree.parse("elreg_app/regions.xml")
    names = tree.xpath('/regions/region/name')
    codes = tree.xpath('/regions/region/code')
    names_codes = zip(names, codes)
    return render_to_response('index.html', {'names_codes': names_codes})