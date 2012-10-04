#coding: utf-8

from django import forms

class PacientForm(forms.Form):
    lastName = forms.CharField()
    firstName = forms.CharField()
    patronymic = forms.CharField()
#    birthday =
#    sex =
#    policy =
    email = forms.EmailField(required=False)