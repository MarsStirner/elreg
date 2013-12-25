# -*- coding: utf-8 -*-
from wtforms.validators import ValidationError
from datetime import datetime


class DateValidator(object):
    def __init__(self, month, day, message=None):
        self.month_fieldname = month
        self.day_fieldname = day
        if not message:
            message = u'Некорректная дата рождения'
        self.message = message

    def __call__(self, form, field):
        try:
            month = form[self.month_fieldname]
            day = form[self.day_fieldname]
        except KeyError, e:
            raise ValidationError(field.gettext(u"Invalid field name (%s).") % e)
        try:
            date = datetime(year=field.data, month=month.data, day=day.data)
            if date > datetime.today():
                ValidationError(self.message)
        except ValueError:
            raise ValidationError(self.message)
        except Exception:
            raise ValidationError(self.message)