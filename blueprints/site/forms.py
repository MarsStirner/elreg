# -*- coding: utf-8 -*-
from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, IntegerField, RadioField, SelectField, BooleanField, FormField
from wtforms.validators import DataRequired, Email, AnyOf, Optional, Required
from application.lib.captcha.fields import CaptchaField


class BirthdayForm(Form):
    day = IntegerField(u'День', [DataRequired(u'Обязательное поле')])
    month = IntegerField(u'Месяц', [DataRequired(u'Обязательное поле')])
    year = IntegerField(u'Год', [DataRequired(u'Обязательное поле')])


class EnqueuePatientForm(Form):
    lastname = StringField(u'Фамилия<span class="text-error">*</span>', [DataRequired()])
    firstname = StringField(u'Имя<span class="text-error">*</span>', [DataRequired()])
    patronymic = StringField(u'Отчество<span class="text-error">*</span>', [DataRequired()])
    #BirthdayForm = FormField(BirthdayForm, label=u'Дата рождения')
    day = IntegerField(u'День рождения<span class="text-error">*</span>', [DataRequired(u'Обязательное поле')])
    month = IntegerField(u'Месяц рождения<span class="text-error">*</span>', [DataRequired(u'Обязательное поле')])
    year = IntegerField(u'Год рождения<span class="text-error">*</span>', [DataRequired(u'Обязательное поле')])
    gender = RadioField(u'Пол<span class="text-error">*</span>',
                        [Required()],
                        choices=[(u'1', u'М'), (u'2', u'Ж')])
    document_type = SelectField(u'Тип документа<span class="text-error">*</span>',
                                [DataRequired()],
                                choices=[('', u'- укажите тип документа -'),
                                         ('client_id', u'Электронная амбулаторная карта'),
                                         ('doc_type_7', u'Военный билет'),
                                         ('policy_type_3', u'Полис ДМС'),
                                         ('policy_type_2', u'Полис ОМС (старого образца)'),
                                         ('policy_type_4', u'Полис ОМС (нового образца)'),
                                         ('doc_type_4', u'Удостоверение личности офицера')])
    send_email = BooleanField(u'отправить информацию о записи на электронный адрес')
    email = StringField(u'Адрес электронной почты', [Optional(), Email(u'Введён некорректный email')])
    confirm = BooleanField()
    series = StringField(u'Серия полиса<span class="text-error">*</span>')
    number = StringField(u'Номер полиса<span class="text-error">*</span>')
    policy_number = StringField(u'Номер полиса<span class="text-error">*</span>')
    client_id = StringField(u'Электронная амбулаторная карта<span class="text-error">*</span>')
    doc_series = StringField(u'Серия документа<span class="text-error">*</span>')
    doc_number = StringField(u'Номер документа<span class="text-error">*</span>')
    captcha = CaptchaField(u'Сосчитайте результат выражения<span class="text-error">*</span>')

