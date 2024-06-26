"""Added log_id field to notification

Revision ID: 6638db147bbb
Revises: 38f83a8a363e
Create Date: 2024-02-10 18:40:35.473738

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6638db147bbb'
down_revision = '38f83a8a363e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_notifications', sa.Column('log_id', sa.Uuid(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service_notifications', 'log_id')
    # ### end Alembic commands ###
