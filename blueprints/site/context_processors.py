# -*- coding: utf-8 -*-
from .app import module
from .lib.utils import _config, datetime_now


@module.context_processor
def header():
    return dict(site_name=_config('SITE_NAME'),
                region_name=_config('REGION_NAME'),
                logo=_config('LOGO_FILE'),
                now=datetime_now(),
                counter=_config('COUNTER_CODE'),
                home_link=_config('HOME_LINK'))