# -*- coding: utf-8 -*-
from datetime import datetime
from database import db
from flask_login import UserMixin

TABLE_PREFIX = 'app'


class Settings(db.Model):
    __tablename__ = '%s_settings' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(25), unique=True, nullable=False)
    name = db.Column(db.Unicode(250), unique=True, nullable=False)
    value = db.Column(db.Unicode(250))
    value_type = db.Column(db.Enum(*{'bool', 'enum', 'string', 'number', 'image'}))

    def __unicode__(self):
        return self.name


class Roles(db.Model):
    __tablename__ = '%s_roles' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), unique=True)
    name = db.Column(db.Unicode(80), unique=True)
    description = db.Column(db.Unicode(255))


class Users(db.Model, UserMixin):
    __tablename__ = '%s_users' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    roles = db.relationship(Roles,
                            secondary='%s_users_roles' % TABLE_PREFIX,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, login, password):
        self.login = login
        self.password = password


class UsersRoles(db.Model):
    __tablename__ = '%s_users_roles' % TABLE_PREFIX

    user_id = db.Column(db.Integer, db.ForeignKey(Users.id), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey(Roles.id), primary_key=True)


class Tickets(db.Model):
    __tablename__ = '%s_tickets' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Unicode(100))
    ticket_uid = db.Column(db.Unicode(40))
    info = db.Column(db.UnicodeText())
    created = db.Column(db.DateTime(), default=datetime.now)
    updated = db.Column(db.DateTime(), nullable=True)
    is_active = db.Column(db.Boolean(), default=True)


class TicketsBlocked(db.Model):
    __tablename__ = '%s_tickets_blocked' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_uid = db.Column(db.Unicode(40))
    lpu_id = db.Column(db.Integer, nullable=False, index=True)
    department_id = db.Column(db.Integer, nullable=False, index=True)
    doctor_id = db.Column(db.Integer, nullable=False, index=True)
    d = db.Column(db.Unicode(10))
    s = db.Column(db.Unicode(10))
    f = db.Column(db.Unicode(10))
    timeslot = db.Column(db.DateTime(), nullable=False)
    timeIndex = db.Column(db.Integer, nullable=True)
    created = db.Column(db.DateTime(), default=datetime.now)
    status = db.Column(db.Enum(*{'blocked', 'free', 'locked', 'disabled'}))
    updated = db.Column(db.DateTime(), nullable=True)
