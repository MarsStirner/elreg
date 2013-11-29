# -*- coding: utf-8 -*-
"""add defaults column to settings

Revision ID: 389bcfa5296b
Revises: 5ae435f83283
Create Date: 2013-11-28 18:15:55.215301

"""

# revision identifiers, used by Alembic.
revision = '389bcfa5296b'
down_revision = '5ae435f83283'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from application.models import Settings


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    try:
        op.add_column('app_settings', sa.Column('defaults', sa.UnicodeText(), nullable=True))
    except Exception, e:
        print e
    try:
        op.alter_column('app_settings', sa.Column('value', sa.UnicodeText(), nullable=True), existing_type=sa.Unicode)
    except Exception, e:
        print e
    try:
        op.alter_column('app_settings', sa.Column('value_type', sa.Enum(*{'bool', 'enum', 'string', 'number', 'image', 'password', 'text'})), existing_type=sa.Enum)
    except Exception, e:
        print e
    op.bulk_insert(Settings.__table__, [
        {'id': 15, 'code': 'COUNTER_CODE', 'name': u'Код счётчика (Яндекс.Метрика)', 'value_type': 'text'}]
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('app_settings', 'defaults')
    op.alter_column('app_settings', sa.Column('value', sa.Unicode(250), nullable=True), existing_type=sa.UnicodeText)
    op.alter_column('app_settings', sa.Column('value_type', sa.Enum(*{'bool', 'enum', 'string', 'number', 'image', 'password'})), existing_type=sa.Enum)
    op.execute(Settings.__table__.delete().where(Settings.id == 15))
    ### end Alembic commands ###
