# -*- coding: utf-8 -*-
import os
import sys
import argparse
import exceptions
from sqlalchemy.ext.serializer import dumps
backups_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'alembic', 'backups'))

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from application.app import app, db


def backup(model):
    serialized_data = dumps(db.session.query(model).all())
    f = open(os.path.join(backups_dir, model.name), 'wb')
    f.write(serialized_data)
    f.close()


parser = argparse.ArgumentParser(description='Backup table data')
parser.add_argument('-t', dest='table', help='Name of DB table to backup (например, tfoms_tag)')
args = parser.parse_args()

table_name = args.table

with app.app_context():
    if table_name and table_name in db.metadata.tables.keys():
        try:
            backup(db.metadata.tables[table_name])
        except exceptions.Exception, e:
            print e
    else:
        print u'Не найдена таблица с указанным именем "%s"' % table_name