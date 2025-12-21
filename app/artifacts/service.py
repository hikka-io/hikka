from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Artifact, User
from sqlalchemy import select


async def get_artifact(
    session: AsyncSession, name: str, user: User
) -> Artifact | None:
    return await session.scalar(
        select(Artifact).filter(
            Artifact.user == user,
            Artifact.name == name,
        )
    )
