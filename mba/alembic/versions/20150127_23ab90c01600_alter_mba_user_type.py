"""alter mba user type

Revision ID: 23ab90c01600
Revises: 55ece74935c5
Create Date: 2015-01-27 16:23:43.190170

"""

# revision identifiers, used by Alembic.
revision = '23ab90c01600'
down_revision = '57fecf5dbd62'

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.execute("update mba_users set type=0")


    op.alter_column('mba_users', 'type',
                    type_=sa.Integer(),
                    server_default=0, #USER_TYPE_MBA
                    existing_type=sa.String(50),
                    nullable=False)


def downgrade():


    op.alter_column('mba_users', 'type',
                type_=sa.String(50),
                server_default='mba_users',
                existing_type=sa.Integer,
                nullable=True)

    op.execute("update mba_users set type='mba_users'")