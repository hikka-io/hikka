"""Removed title_native field

Revision ID: 3ef5732b5d63
Revises: 7f8d427770eb
Create Date: 2024-06-21 01:26:33.410121

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3ef5732b5d63'
down_revision = '7f8d427770eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_favourite_anime')
    op.add_column('service_content_anime_episodes', sa.Column('title_original', sa.String(), nullable=True))
    op.drop_column('service_content_anime_episodes', 'title_native')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_content_anime_episodes', sa.Column('title_native', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('service_content_anime_episodes', 'title_original')
    op.create_table('service_favourite_anime',
    sa.Column('anime_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['anime_id'], ['service_content_anime.id'], name='service_favourite_anime_anime_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['service_users.id'], name='service_favourite_anime_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='service_favourite_anime_pkey'),
    sa.UniqueConstraint('anime_id', 'user_id', name='service_favourite_anime_anime_id_user_id_key')
    )
    # ### end Alembic commands ###
