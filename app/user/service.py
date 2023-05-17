from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User


async def change_description(
    session: AsyncSession, user: User, description: str
) -> User:
    user.description = description

    session.add(user)
    await session.commit()

    return user
