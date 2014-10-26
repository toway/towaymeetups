"""add_banner

Revision ID: 37df2a153359
Revises: 2633bb4ca08d
Create Date: 2014-09-17 22:17:24.795000

"""
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '37df2a153359'
down_revision = '2633bb4ca08d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'banners',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('banner_position', sa.Integer, default=0),
        sa.Column('type', sa.Integer, default=0),
        sa.Column('title', sa.String(100) ),
        sa.Column('img_url', sa.String(100) ),
        sa.Column('link_url', sa.String(100) ),        
        sa.Column('htmlcontent', sa.String(500) , default=0),  
        sa.Column('last_edit_date', sa.String(100) ,default=datetime.now(tz=None).date()),
        sa.Column('status', sa.Integer , default=1)       
    )
  


def downgrade():
    op.drop_table('banners')
