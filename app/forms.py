# -*- coding: utf-8 -*-
from wtforms import TextField, BooleanField, PasswordField, RadioField
from wtforms.validators import Required
from flask_wtf import Form


class EditUserForm(Form):

    login = TextField(u'Логин', validators=[Required()], default="")
    password = PasswordField(u'Пароль', default="")
    password_reply = PasswordField(u'Повторите пароль', default="")
    role = RadioField(u'Роль', coerce=int)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.password.data and self.password_reply.data and self.password.data != self.password_reply.data:
            self.password.errors.append(u'Пароли не совпадают')
            self.password_reply.errors.append(u'Пароли не совпадают')
            return False
        return True


class LoginForm(Form):
    login = TextField(u'Логин')
    password = PasswordField(u'Пароль')