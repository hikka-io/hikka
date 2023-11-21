from sqlalchemy.ext.asyncio import AsyncSession
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

    user.username = username

    session.add(user)
    await session.commit()

    return user
