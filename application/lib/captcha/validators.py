# -*- coding: utf-8 -*-
from flask import request, current_app, session


class CaptchaValidator(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if self.message is None:
            self.message = u'Введён неверный проверочный код'
        if current_app.testing:
            return
        captcha_id = request.form.get('{name}_id'.format(field.name), '')
        challenge = field.data.lower().strip()
        key = 'captcha_{id}'.format(id=captcha_id)
        captcha = session.get(key)
        response = captcha.get('response')
        if not response or response != challenge:
            raise ValueError(self.message)
        if key in session:
            del session[key]