"""Added deleted field to comment

Revision ID: 96bbdfce77ce
Revises: dc741ff7e111
Create Date: 2024-01-28 01:22:14.719149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "96bbdfce77ce"
down_revision = "dc741ff7e111"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "service_comments",
        sa.Column(
            "deleted",
            sa.Boolean(),
            server_default=sa.schema.DefaultClause("false"),
            nullable=False,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("service_comments", "deleted")
    # ### end Alembic commands ###
