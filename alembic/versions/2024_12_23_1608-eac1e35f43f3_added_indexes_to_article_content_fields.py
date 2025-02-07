"""Added indexes to article content fields

Revision ID: eac1e35f43f3
Revises: c448e3d92c92
Create Date: 2024-12-23 16:08:00.443087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eac1e35f43f3'
down_revision = 'c448e3d92c92'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_service_articles_content_id'), 'service_articles', ['content_id'], unique=False)
    op.create_index(op.f('ix_service_articles_content_type'), 'service_articles', ['content_type'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_service_articles_content_type'), table_name='service_articles')
    op.drop_index(op.f('ix_service_articles_content_id'), table_name='service_articles')
    # ### end Alembic commands ###
