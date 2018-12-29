"""rename isStation to is_station

Revision ID: 8ffaab230d3e
Revises: 55ca2c0b5330
Create Date: 2018-12-29 20:12:38.084065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ffaab230d3e'
down_revision = '55ca2c0b5330'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('stop', 'isStation', new_column_name='is_station')


def downgrade():
    op.alter_column('stop', 'is_station', new_column_name='isStation')
