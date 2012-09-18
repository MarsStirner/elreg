#!/usr/bin/env python

from django.shortcuts import render_to_response

def index(request):
    return render_to_response('lpu_regions.html')