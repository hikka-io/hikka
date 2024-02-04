from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Anime
from app.errors import Abort
from fastapi import Depends
from uuid import UUID
from . import service


async def validate_watari_anime(
    slug: UUID, session: AsyncSession = Depends(get_session)
) -> Anime:
    if not (anime := await service.get_anime_by_watari(session, slug)):
        raise Abort("anime", "not-found")

    return anime
