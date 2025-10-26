
"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-10-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE SCHEMA IF NOT EXISTS ideabridge')

def downgrade():
    op.execute('DROP SCHEMA IF EXISTS ideabridge CASCADE')
