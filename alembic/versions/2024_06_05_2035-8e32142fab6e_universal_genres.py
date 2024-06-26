"""Universal genres

Revision ID: 8e32142fab6e
Revises: 2dbc8e451a4f
Create Date: 2024-06-05 20:35:31.476199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e32142fab6e'
down_revision = '2dbc8e451a4f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_content_genres',
    sa.Column('name_en', sa.String(length=64), nullable=True),
    sa.Column('name_ua', sa.String(length=64), nullable=True),
    sa.Column('type', sa.String(length=32), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('content_id', sa.String(length=36), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_content_genres_content_id'), 'service_content_genres', ['content_id'], unique=True)
    op.create_index(op.f('ix_service_content_genres_slug'), 'service_content_genres', ['slug'], unique=False)
    op.create_index(op.f('ix_service_content_genres_type'), 'service_content_genres', ['type'], unique=False)
    op.create_table('service_relation_genres_anime',
    sa.Column('anime_id', sa.Uuid(), nullable=False),
    sa.Column('genre_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['anime_id'], ['service_content_anime.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['service_content_genres.id'], ),
    sa.PrimaryKeyConstraint('anime_id', 'genre_id')
    )
    op.create_table('service_relation_genres_manga',
    sa.Column('manga_id', sa.Uuid(), nullable=False),
    sa.Column('genre_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['service_content_genres.id'], ),
    sa.ForeignKeyConstraint(['manga_id'], ['service_content_manga.id'], ),
    sa.PrimaryKeyConstraint('manga_id', 'genre_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_relation_genres_manga')
    op.drop_table('service_relation_genres_anime')
    op.drop_index(op.f('ix_service_content_genres_type'), table_name='service_content_genres')
    op.drop_index(op.f('ix_service_content_genres_slug'), table_name='service_content_genres')
    op.drop_index(op.f('ix_service_content_genres_content_id'), table_name='service_content_genres')
    op.drop_table('service_content_genres')
    # ### end Alembic commands ###
