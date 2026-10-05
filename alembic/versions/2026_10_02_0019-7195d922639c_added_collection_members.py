"""Added collection members

Revision ID: 7195d922639c
Revises: 3778d7981774
Create Date: 2026-10-02 00:19:28.240244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7195d922639c"
down_revision = "3778d7981774"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_collection_members",
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("owner_offered_at", sa.DateTime(), nullable=True),
        sa.Column("collection_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("invited_by_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["collection_id"], ["service_collections.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["invited_by_id"], ["service_users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["service_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_id", "user_id"),
    )
    # Collection must never have more than one owner
    op.create_index(
        "ix_collection_member_owner",
        "service_collection_members",
        ["collection_id"],
        unique=True,
        postgresql_where=sa.text("role = 'owner'"),
    )
    # Collections of a given user: the author filter and the owner quota
    op.create_index(
        "ix_collection_member_user",
        "service_collection_members",
        ["user_id", "status"],
        unique=False,
    )
    # At most one ownership offer may stand per collection
    op.create_index(
        "ix_collection_member_owner_offer",
        "service_collection_members",
        ["collection_id"],
        unique=True,
        postgresql_where=sa.text("owner_offered_at IS NOT NULL"),
    )

    # Backfill: every existing collection author becomes its owner.
    # Soft deleted collections are migrated too, otherwise they would end up
    # without an owner and diverge from author_id.
    # NOTE: author_id is nullable, collections without an author stay
    # ownerless: public and unlisted ones can only be edited by moderators,
    # private ones are unreachable for everyone
    op.execute(
        """
        INSERT INTO service_collection_members
            (id, collection_id, user_id, role, status, created, updated)
        SELECT gen_random_uuid(), id, author_id, 'owner', 'accepted',
               created, created
        FROM service_collections
        WHERE author_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_collection_member_owner_offer",
        table_name="service_collection_members",
        postgresql_where=sa.text("owner_offered_at IS NOT NULL"),
    )
    op.drop_index(
        "ix_collection_member_user",
        table_name="service_collection_members",
    )
    op.drop_index(
        "ix_collection_member_owner",
        table_name="service_collection_members",
        postgresql_where=sa.text("role = 'owner'"),
    )
    op.drop_table("service_collection_members")
