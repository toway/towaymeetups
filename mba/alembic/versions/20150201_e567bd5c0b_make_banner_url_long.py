"""make banner url longger

Revision ID: e567bd5c0b
Revises: 23ab90c01600
Create Date: 2015-02-01 13:15:59.075956

"""

# revision identifiers, used by Alembic.
revision = 'e567bd5c0b'
down_revision = '23ab90c01600'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('banners', 'link_url',
                    type_=sa.String(200),
                    existing_type=sa.String(100),
                    nullable=True)


def downgrade():
    pass
