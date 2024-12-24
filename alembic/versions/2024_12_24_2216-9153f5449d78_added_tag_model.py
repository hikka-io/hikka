"""Added tag model

Revision ID: 9153f5449d78
Revises: d24be66ce4d7
Create Date: 2024-12-24 22:16:41.502871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9153f5449d78'
down_revision = 'd24be66ce4d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_tags',
    sa.Column('content_count', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('content_type', sa.String(), nullable=False),
    sa.Column('content_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_tags_content_count'), 'service_tags', ['content_count'], unique=False)
    op.create_index(op.f('ix_service_tags_name'), 'service_tags', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_service_tags_name'), table_name='service_tags')
    op.drop_index(op.f('ix_service_tags_content_count'), table_name='service_tags')
    op.drop_table('service_tags')
    # ### end Alembic commands ###