"""Updated collections stuff

Revision ID: 9d59170b2da4
Revises: 49691627cab8
Create Date: 2024-02-21 01:24:38.103398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d59170b2da4'
down_revision = '49691627cab8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_collection_group_content',
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('content_type', sa.String(), nullable=False),
    sa.Column('content_id', sa.Uuid(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('service_collections', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('service_collections', 'description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_table('service_collection_group_content')
    # ### end Alembic commands ###
