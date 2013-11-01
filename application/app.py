# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.principal import Principal
from flask.ext.babel import Babel
import pytz
from database import db
import config

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
from models import *

babel = Babel(app)

from lib.utils import create_config_func
_config = create_config_func()
app.config.update(
    MAIL_SERVER=_config('EMAIL_HOST'),
    MAIL_PORT=_config('EMAIL_PORT'),
    MAIL_USERNAME=_config('EMAIL_HOST_USER'),
    MAIL_PASSWORD=_config('EMAIL_HOST_PASSWORD'),
    MAIL_USE_TLS=_config('EMAIL_USE_TLS'),
    MAIL_DEFAULT_SENDER=_config('DEFAULT_FROM_EMAIL')
)

@babel.timezoneselector
def get_timezone():
    return pytz.timezone(_config('TIME_ZONE'))

from blueprints.site.app import module as site
app.register_blueprint(site)

from lib.utils import login_manager
Principal(app)
login_manager.init_app(app)

# Import all views
import views