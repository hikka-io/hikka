"""Collections needs_search_update

Revision ID: 855b2f3b994b
Revises: f5c9d858fc15
Branch Labels: None
Depends On: None

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "855b2f3b994b"
down_revision = "f5c9d858fc15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "service_collections",
        sa.Column(
            "needs_search_update",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.execute(
        "UPDATE service_collections SET needs_search_update = TRUE "
        "WHERE visibility = 'public'"
    )


def downgrade() -> None:
    op.drop_column("service_collections", "needs_search_update")
