"""Added views to article

Revision ID: 8a9077498cf4
Revises: a339e6f4ac12
Create Date: 2025-03-03 03:56:56.210959

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8a9077498cf4"
down_revision = "a339e6f4ac12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "service_articles",
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("service_articles", "views")
    # ### end Alembic commands ###
