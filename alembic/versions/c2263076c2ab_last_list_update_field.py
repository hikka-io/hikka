"""Last list update field

Revision ID: c2263076c2ab
Revises: 1dd385e4cf87
Create Date: 2023-12-26 02:45:09.814178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2263076c2ab'
down_revision = '1dd385e4cf87'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_users', sa.Column('last_list_update', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service_users', 'last_list_update')
    # ### end Alembic commands ###
