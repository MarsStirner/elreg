#!/usr/bin/env python

from django.shortcuts import render_to_response
import datetime

def index(request):
    now = datetime.datetime.now()
    return render_to_response('index.html', locals())