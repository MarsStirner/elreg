# -*- coding: utf-8 -*-
from hashlib import sha256
from flask import session, current_app
from wtforms.validators import Required
from wtforms.fields import StringField
from .widgets import Captcha as CaptchaWidget
from .validators import CaptchaValidator
from .conf.settings import get_challenge


class CaptchaField(StringField):
    widget = CaptchaWidget()

    def __init__(self, label='', validators=None, **kwargs):
        validators = validators or [Required(), CaptchaValidator()]
        super(CaptchaField, self).__init__(label, validators, **kwargs)
        self.captcha_id = self.generate_id()

    def generate_id(self):
        challenge, response = get_challenge()()

        captcha_id = sha256('{0}{1}'.format(current_app.config["SECRET_KEY"], response)).hexdigest()
        session['captcha_{id}'.format(id=captcha_id)] = dict(challenge=challenge, response=response)
        return captcha_id