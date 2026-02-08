from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Digest, User
from sqlalchemy import select


async def get_digest(
    session: AsyncSession, name: str, user: User
) -> Digest | None:
    return await session.scalar(
        select(Digest).filter(
            Digest.user == user,
            Digest.name == name,
        )
    )


async def set_privacy(session: AsyncSession, digest: Digest, private: bool):
    digest.private = private
    await session.commit()
    return digest
