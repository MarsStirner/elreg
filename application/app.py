# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.principal import Principal
from database import db
import config

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
from models import *

from blueprints.site.app import module as site
app.register_blueprint(site)

from lib.utils import login_manager
Principal(app)
login_manager.init_app(app)

# Import all views
import views