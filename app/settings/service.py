from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import hashpwd
from datetime import datetime
from app.models import User


async def change_description(
    session: AsyncSession, user: User, description: str
) -> User:
    """Change description"""

    user.description = description if description else None

    session.add(user)
    await session.commit()

    return user


async def set_username(session: AsyncSession, user: User, username: str):
    """Changed username"""

    user.last_username_change = datetime.utcnow()
    user.username = username

    session.add(user)
    await session.commit()

    return user


async def set_email(session: AsyncSession, user: User, email: str):
    """Changed email"""

    user.last_email_change = datetime.utcnow()
    user.email_confirmed = False
    user.email = email

    session.add(user)
    await session.commit()

    return user


async def set_password(session: AsyncSession, user: User, password: str):
    """Changed password"""

    user.password_hash = hashpwd(password)

    session.add(user)
    await session.commit()

    return user
