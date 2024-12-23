"""Added article content

Revision ID: 3f1664c50dd2
Revises: 7a805de5e5d8
Create Date: 2024-11-20 23:34:25.032540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f1664c50dd2'
down_revision = '7a805de5e5d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_articles_content',
    sa.Column('content_type', sa.String(), nullable=False),
    sa.Column('content_id', sa.Uuid(), nullable=False),
    sa.Column('article_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['service_articles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_index('ix_service_articles_slug', table_name='service_articles')
    op.create_index(op.f('ix_service_articles_slug'), 'service_articles', ['slug'], unique=True)
    op.drop_index('ix_service_content_anime_slug', table_name='service_content_anime')
    op.create_index(op.f('ix_service_content_anime_slug'), 'service_content_anime', ['slug'], unique=True)
    op.drop_index('ix_service_content_anime_staff_roles_slug', table_name='service_content_anime_staff_roles')
    op.create_index(op.f('ix_service_content_anime_staff_roles_slug'), 'service_content_anime_staff_roles', ['slug'], unique=True)
    op.drop_index('ix_service_content_author_roles_slug', table_name='service_content_author_roles')
    op.create_index(op.f('ix_service_content_author_roles_slug'), 'service_content_author_roles', ['slug'], unique=True)
    op.drop_index('ix_service_content_characters_slug', table_name='service_content_characters')
    op.create_index(op.f('ix_service_content_characters_slug'), 'service_content_characters', ['slug'], unique=True)
    op.drop_index('ix_service_content_companies_slug', table_name='service_content_companies')
    op.create_index(op.f('ix_service_content_companies_slug'), 'service_content_companies', ['slug'], unique=True)
    op.drop_index('ix_service_content_genres_slug', table_name='service_content_genres')
    op.create_index(op.f('ix_service_content_genres_slug'), 'service_content_genres', ['slug'], unique=True)
    op.drop_index('ix_service_content_magazines_slug', table_name='service_content_magazines')
    op.create_index(op.f('ix_service_content_magazines_slug'), 'service_content_magazines', ['slug'], unique=True)
    op.drop_index('ix_service_content_manga_slug', table_name='service_content_manga')
    op.create_index(op.f('ix_service_content_manga_slug'), 'service_content_manga', ['slug'], unique=True)
    op.drop_index('ix_service_content_novel_slug', table_name='service_content_novel')
    op.create_index(op.f('ix_service_content_novel_slug'), 'service_content_novel', ['slug'], unique=True)
    op.drop_index('ix_service_content_people_slug', table_name='service_content_people')
    op.create_index(op.f('ix_service_content_people_slug'), 'service_content_people', ['slug'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_service_content_people_slug'), table_name='service_content_people')
    op.create_index('ix_service_content_people_slug', 'service_content_people', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_novel_slug'), table_name='service_content_novel')
    op.create_index('ix_service_content_novel_slug', 'service_content_novel', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_manga_slug'), table_name='service_content_manga')
    op.create_index('ix_service_content_manga_slug', 'service_content_manga', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_magazines_slug'), table_name='service_content_magazines')
    op.create_index('ix_service_content_magazines_slug', 'service_content_magazines', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_genres_slug'), table_name='service_content_genres')
    op.create_index('ix_service_content_genres_slug', 'service_content_genres', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_companies_slug'), table_name='service_content_companies')
    op.create_index('ix_service_content_companies_slug', 'service_content_companies', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_characters_slug'), table_name='service_content_characters')
    op.create_index('ix_service_content_characters_slug', 'service_content_characters', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_author_roles_slug'), table_name='service_content_author_roles')
    op.create_index('ix_service_content_author_roles_slug', 'service_content_author_roles', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_anime_staff_roles_slug'), table_name='service_content_anime_staff_roles')
    op.create_index('ix_service_content_anime_staff_roles_slug', 'service_content_anime_staff_roles', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_content_anime_slug'), table_name='service_content_anime')
    op.create_index('ix_service_content_anime_slug', 'service_content_anime', ['slug'], unique=False)
    op.drop_index(op.f('ix_service_articles_slug'), table_name='service_articles')
    op.create_index('ix_service_articles_slug', 'service_articles', ['slug'], unique=False)
    op.drop_table('service_articles_content')
    # ### end Alembic commands ###
