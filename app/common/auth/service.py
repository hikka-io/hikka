from sqlalchemy import select, exists, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app import constants


def normalize_email(email: str) -> str:
    """Return address all aliases of the same mailbox share"""

    # Don't change this once released since stored normalized emails
    # are compared against what it returns
    email = email.strip().lower()

    if "@" not in email:
        return email

    local, domain = email.split("@", 1)

    if domain in constants.EMAIL_PLUS_DOMAINS:
        local = local.split("+", 1)[0]

    if domain in constants.EMAIL_GMAIL_DOMAINS:
        local = local.replace(".", "")
        domain = "gmail.com"

    return f"{local}@{domain}"


async def is_email_taken(session: AsyncSession, email: str) -> bool:
    """Check whether any account uses this address or its mailbox"""

    return await session.scalar(
        select(
            exists().where(
                or_(
                    func.lower(User.email) == email.lower(),
                    User.email_normalized == normalize_email(email),
                )
            )
        )
    )
