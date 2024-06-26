"""Added updated field to user

Revision ID: 700c99947427
Revises: c2263076c2ab
Create Date: 2023-12-26 03:02:19.808475

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '700c99947427'
down_revision = 'c2263076c2ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_users', sa.Column('updated', sa.DateTime(), nullable=True))
    op.drop_column('service_users', 'last_list_update')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_users', sa.Column('last_list_update', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('service_users', 'updated')
    # ### end Alembic commands ###
