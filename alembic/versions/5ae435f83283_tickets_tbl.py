"""Tickets tbl

Revision ID: 5ae435f83283
Revises: 8bc86434f7
Create Date: 2013-11-05 11:19:33.176885

"""

# revision identifiers, used by Alembic.
revision = '5ae435f83283'
down_revision = '8bc86434f7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    from application.app import db, app
    with app.app_context():
        db.create_all()


def downgrade():
    from application.models import Tickets
    op.drop_table(Tickets.__tablename__)
