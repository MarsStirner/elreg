# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.tz import tzlocal
from pytz import timezone
from .app import module
from .lib.utils import _config


@module.context_processor
def header():
    return dict(site_name=_config('SITE_NAME'),
                region_name=_config('REGION_NAME'),
                logo=_config('LOGO_FILE'),
                now=datetime.now(tzlocal()).astimezone(tz=timezone(_config('TIME_ZONE'))).replace(tzinfo=None),
                home_link=_config('HOME_LINK'))