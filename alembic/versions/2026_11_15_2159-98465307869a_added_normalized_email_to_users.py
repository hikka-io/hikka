"""Added normalized email to users

Revision ID: 98465307869a
Revises: 5de1b2158e6c
Create Date: 2026-11-15 21:59:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "98465307869a"
down_revision = "5de1b2158e6c"
branch_labels = None
depends_on = None


# Copy of normalization rules at the time of this migration
plus_domains = {
    "gmail.com",
    "googlemail.com",
    "yahoo.com",
    "ymail.com",
    "rocketmail.com",
    "protonmail.com",
    "protonmail.ch",
    "proton.me",
    "pm.me",
    "icloud.com",
    "me.com",
    "mac.com",
}

gmail_domains = {"gmail.com", "googlemail.com"}


def normalize_email(email: str) -> str:
    email = email.strip().lower()

    if "@" not in email:
        return email

    local, domain = email.split("@", 1)

    if domain in plus_domains:
        local = local.split("+", 1)[0]

    if domain in gmail_domains:
        local = local.replace(".", "")
        domain = "gmail.com"

    return f"{local}@{domain}"


def upgrade() -> None:
    op.add_column(
        "service_users",
        sa.Column("email_normalized", sa.String(length=255), nullable=True),
    )

    connection = op.get_bind()

    users = connection.execute(
        sa.text("SELECT id, email FROM service_users WHERE email IS NOT NULL")
    ).all()

    if users:
        connection.execute(
            sa.text(
                "UPDATE service_users SET email_normalized = :email_normalized "
                "WHERE id = :id"
            ),
            [
                {"id": user.id, "email_normalized": normalize_email(user.email)}
                for user in users
            ],
        )

    # Not unique since accounts created before this share some mailboxes
    op.create_index(
        "ix_service_users_email_normalized",
        "service_users",
        ["email_normalized"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_users_email_normalized",
        table_name="service_users",
    )

    op.drop_column("service_users", "email_normalized")
