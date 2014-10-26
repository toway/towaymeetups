"""use mba alembic version

Revision ID: 2633bb4ca08d
Revises: None
Create Date: 2014-09-14 12:42:44.023000

"""

# revision identifiers, used by Alembic.
revision = '2633bb4ca08d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    #op.drop_table('kotti_alembic_version')    
    pass


def downgrade():
    pass
