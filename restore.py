# -*- coding: utf-8 -*-
import os
import sys
from sqlalchemy import exc
from sqlalchemy.ext.serializer import loads
from sqlalchemy import func
from application.app import app, db


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
backups_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'alembic', 'backups'))


def restore():
    disable_fk(db.session.bind.engine.url.drivername)
    for bk_file in os.listdir(backups_dir):
        file_path = os.path.join(backups_dir, bk_file)
        if not os.path.isfile(file_path):
            continue
        f = open(file_path, 'rb')
        data = f.read()
        data_list = loads(data)
        model = db.metadata.tables[bk_file]
        try:
            db.session.execute(model.insert().values(data_list))
        except exc.IntegrityError, e:
            print e
            db.session.rollback()
        except exc.InternalError, e:
            print e
            db.session.rollback()
        else:
            db.session.commit()
            __restore_sequence(db.session.bind.engine.url.drivername, model)

    enable_fk(db.session.bind.engine.url.drivername)
    db.session.remove()


def __restore_sequence(driver, table):
    if driver.find('postgresql') > -1:
        db.session.execute('''SELECT setval('{0}_id_seq', (SELECT max(id) FROM {0}))'''.format(table))
        db.session.commit()


def disable_fk(driver):
    if driver == 'mysql':
        db.session.execute('SET FOREIGN_KEY_CHECKS=0')
    elif driver.find('postgresql') > -1:
        db.session.execute('SET CONSTRAINTS ALL DEFERRED')


def enable_fk(driver):
    if driver == 'mysql':
        db.session.execute('SET FOREIGN_KEY_CHECKS=1')
    elif driver.find('postgresql') > -1:
        pass


if __name__ == '__main__':
    with app.app_context():
        restore()