"""Added edit stats mode

Revision ID: 8da1c939c781
Revises: a0e9c850132e
Create Date: 2024-03-16 19:44:53.160357

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8da1c939c781'
down_revision = 'a0e9c850132e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_stats_edits',
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('create', sa.Integer(), nullable=False),
    sa.Column('update', sa.Integer(), nullable=False),
    sa.Column('accept', sa.Integer(), nullable=False),
    sa.Column('close', sa.Integer(), nullable=False),
    sa.Column('deny', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['service_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_stats_edits')
    # ### end Alembic commands ###
