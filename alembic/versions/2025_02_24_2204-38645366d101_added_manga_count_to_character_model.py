"""Added manga_count to character model

Revision ID: 38645366d101
Revises: 80a4c31dfa1e
Create Date: 2025-02-24 22:04:55.652931

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "38645366d101"
down_revision = "80a4c31dfa1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "service_content_characters",
        sa.Column(
            "manga_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("service_content_characters", "manga_count")
    # ### end Alembic commands ###
