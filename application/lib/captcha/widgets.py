# -*- coding: utf-8 -*-
from flask import url_for
from jinja2 import Markup
from wtforms.widgets import TextInput, HTMLString


class Captcha(object):
    def __call__(self, field, **kwargs):
        html = HTMLString(
            u'''<img src="{image}" class="captcha" alt="Проверочное выражение" />
            <input type="hidden" name="{name}_id" value="{captcha_id}" />'''
            .format(image=url_for('get_captcha_image', captcha_id=field.captcha_id),
                    name=field.name,
                    captcha_id=field.captcha_id))
        captcha_field = TextInput()
        return Markup(html + captcha_field(field, maxlength=4, **kwargs))