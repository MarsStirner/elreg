# -*- coding: utf-8 -*-
from threading import Thread
from flask import copy_current_request_context
from jinja2 import Environment, PackageLoader
from flask_mail import Message
from application.app import mail
from ..site.lib.utils import _config, logger
from .app import module


def _generate_ticket_message(template, data, lpu_info, dequeue_link, session):
    env = Environment(loader=PackageLoader(module.import_name,  module.template_folder))
    template = env.get_template(template)
    return template.render(data=data, session=session, lpu=lpu_info, dequeue_link=dequeue_link)


def send_async_email(msg, email):
    @copy_current_request_context
    def send_message(msg, email):
        try:
            mail.send(msg)
        except Exception, e:
            print e
            logger.error(u'Ошибка при отправке письма на адрес: {0}\n{1}'.format(email, e),
                         extra=dict(tags=[u'отправка письма', 'elreg']))
            return False
        return True

    thr = Thread(target=send_message, args=[msg, email])
    thr.start()


def send_ticket(patient_email, data, lpu_info, dequeue_link, session_data):
    message = Message(u'Уведомление о записи на приём',
                      sender=(_config('SITE_NAME'), _config('DEFAULT_FROM_EMAIL')),
                      recipients=[patient_email])
    message.body = _generate_ticket_message('{0}/email/email.txt'.format(module.name),
                                            data, lpu_info, dequeue_link=dequeue_link, session=session_data)
    message.html = _generate_ticket_message('{0}/email/email.html'.format(module.name),
                                            data, lpu_info, dequeue_link=dequeue_link, session=session_data)
    send_async_email(message, patient_email)