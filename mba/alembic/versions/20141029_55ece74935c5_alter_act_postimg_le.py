"""alter act postimg length

Revision ID: 55ece74935c5
Revises: None
Create Date: 2014-10-29 18:21:22.923611

"""

# revision identifiers, used by Alembic.
revision = '55ece74935c5'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('acts', 'poster_img', type_=sa.String(200), existing_type=sa.String(length=50), nullable=True)


def downgrade():
    pass
