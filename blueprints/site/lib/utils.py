# -*- encoding: utf-8 -*-
from application.lib.utils import create_config_func

_config = create_config_func()


def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)