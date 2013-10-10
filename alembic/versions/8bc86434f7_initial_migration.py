"""initial migration

Revision ID: 8bc86434f7
Revises: None
Create Date: 2013-10-09 13:50:43.350093

"""

# revision identifiers, used by Alembic.
revision = '8bc86434f7'
down_revision = None

from alembic import op


def upgrade():
    from application.app import db, app
    from restore import restore
    with app.app_context():
        db.create_all()
        restore()


def downgrade():
    pass
