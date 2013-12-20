# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.principal import Principal
from flask.ext.babel import Babel
from flask_mail import Mail
from flask_beaker import BeakerSession
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
    MAIL_PORT=str(_config('EMAIL_PORT')),
    MAIL_USERNAME=_config('EMAIL_HOST_USER'),
    MAIL_PASSWORD=str(_config('EMAIL_HOST_PASSWORD')),
    MAIL_USE_TLS=bool(_config('EMAIL_USE_TLS')),
    MAIL_USE_SSL=bool(_config('EMAIL_USE_SSL')),
    MAIL_DEFAULT_SENDER=_config('DEFAULT_FROM_EMAIL')
)

mail = Mail(app)
BeakerSession(app)


@babel.timezoneselector
def get_timezone():
    return pytz.timezone(_config('TIME_ZONE'))

from blueprints.site.app import module as site
from blueprints.infokiosk.app import module as infokiosk
app.register_blueprint(site)
app.register_blueprint(infokiosk, url_prefix='/{0}'.format(infokiosk.name))

from lib.utils import login_manager
Principal(app)
login_manager.init_app(app)

# Import all views
import views