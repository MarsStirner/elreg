# -*- coding: utf-8 -*-
from livesettings import config_register, config_register_list
from livesettings.values import *
from custom_livesettings.values import ImageValue
#from django.utils.translation import ugettext_lazy as _

# First, setup a grup to hold all our possible configs
MAIL_GROUP = ConfigurationGroup(
    'Mail',               # key: internal name of the group to be created
    u'Настройки подключения к почтовому серверу',  # name: verbose name which can be automatically translated
    ordering=0             # ordering: order of group in the list (default is 1)
)

config_register_list(
    StringValue( MAIL_GROUP, 'EMAIL_HOST', description='Email host', ordering=1, default='localhost',
        help_text=u'Сервер исходяще почты'),
    PositiveIntegerValue(MAIL_GROUP, 'EMAIL_PORT', description = 'Email port', ordering=2, default = 1025,
        help_text=u"Порт для исходящей почты"),
    StringValue( MAIL_GROUP, 'EMAIL_HOST_USER', description='Email host user', ordering=3, default='',
        help_text=u'Логин для авторизации на почтовом сервере'),
    PasswordValue( MAIL_GROUP, 'EMAIL_HOST_PASSWORD', description='Email host password', ordering=4, default='',
        render_value=True, help_text=u'Пароль для авторизации на почтовом сервере'),
    BooleanValue( MAIL_GROUP, 'EMAIL_USE_TLS', description=u'Использовать TLS',  ordering=5, default=False,
        help_text=u'Использовать защищенный протокол TLS'),
    StringValue( MAIL_GROUP, 'DEFAULT_FROM_EMAIL', description=u'Email отправки',  ordering=5, default='',
        help_text=u'Email адрес, указываемый в поле письма "От кого:"'),
)

TIME_ZONE = ConfigurationGroup(
    'TZ',               # key: internal name of the group to be created
    u'Региональные настройки',  # name: verbose name which can be automatically translated
    ordering=1             # ordering: order of group in the list (default is 1)
)

config_register_list(
    # Listbox with multiple selection - MultipleStringValue with choices
    StringValue( TIME_ZONE, 'TIME_ZONE',
        description=u'Выбор часовой зоны', ordering=0, help_text=u'Выбор часовой зоны для текущей установки сервиса',
        default='Europe/Moscow',
        choices=(
            ('Europe/Kaliningrad', u'Калининградское время (UTC+3)'),
            ('Europe/Moscow', u'Московское время (UTC+4)'),
            ('Asia/Yekaterinburg', u'Екатеринбургское время (UTC+6)'),
            ('Asia/Omsk', u'Омское время (UTC+7)'),
            ('Asia/Krasnoyarsk', u'Красноярское время (UTC+8)'),
            ('Asia/Irkutsk', u'Иркутское время (UTC+9)'),
            ('Asia/Yakutsk', u'Якутское время (UTC+10)'),
            ('Asia/Vladivostok', u'Владивостокское время (UTC+11)'),
            ('Asia/Magadan', u'Магаданское время (UTC+12)'),
            ),
    ),
    StringValue(TIME_ZONE, 'SITE_NAME',  description=u'Название сайта в шапку', ordering=1,
        help_text=u'Название сайте в шапку', default=u'Портал государственных и муниципальных услуг'),
    StringValue(TIME_ZONE, 'REGION_NAME',  description=u'Наименование региона в шапку', ordering=2,
        help_text=u'Наименование региона в шапку (вторая строка)', default=''),
    ImageValue( TIME_ZONE, 'LOGO_FILE', description=u'Файл логотипа', ordering=3, default='',
        help_text=u'Логотип/герб региона для размещения в шапке страниц'),
)

IS = ConfigurationGroup(
    'IS',               # key: internal name of the group to be created
    u'Интеграционный сервис',  # name: verbose name which can be automatically translated
    ordering=2             # ordering: order of group in the list (default is 1)
)
config_register(
    StringValue(IS, 'URL',  description=u'Адрес интеграционного сервиса',
        help_text=u'Адрес интеграционного сервиса', default="http://84.204.44.39:7023/int-server/index.php?wsdl="),
)
