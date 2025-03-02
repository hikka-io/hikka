"""Added comments_count_pagination to content

Revision ID: a339e6f4ac12
Revises: a34dd7174d66
Create Date: 2025-03-02 20:28:31.778649

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a339e6f4ac12"
down_revision = "a34dd7174d66"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "service_articles",
        sa.Column(
            "comments_count_pagination",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "service_collections",
        sa.Column(
            "comments_count_pagination",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "service_content_anime",
        sa.Column(
            "comments_count_pagination",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "service_content_manga",
        sa.Column(
            "comments_count_pagination",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "service_content_novel",
        sa.Column(
            "comments_count_pagination",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "service_edits",
        sa.Column(
            "comments_count_pagination",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("service_edits", "comments_count_pagination")
    op.drop_column("service_content_novel", "comments_count_pagination")
    op.drop_column("service_content_manga", "comments_count_pagination")
    op.drop_column("service_content_anime", "comments_count_pagination")
    op.drop_column("service_collections", "comments_count_pagination")
    op.drop_column("service_articles", "comments_count_pagination")
    # ### end Alembic commands ###
