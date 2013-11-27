# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.tz import tzlocal
from pytz import timezone
from application.lib.utils import create_config_func
from config import DEBUG
from pysimplelogs.logger import SimpleLogger
from ..config import MODULE_NAME, RUS_NAME
from version import version


_config = create_config_func()

logger = SimpleLogger.get_logger(_config('SIMPLELOGS_URL'),
                                 MODULE_NAME,
                                 dict(name=RUS_NAME, version=version),
                                 DEBUG)


def datetime_now():
    return datetime.now(tzlocal()).astimezone(tz=timezone(_config('TIME_ZONE'))).replace(tzinfo=None)