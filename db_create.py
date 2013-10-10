# -*- coding: utf-8 -*-

#TODO: Add Migrations
#TODO: Add Auto Creation blueprints Tables
from application.app import db, app
with app.app_context():
    db.create_all()