from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Anime
from app.errors import Abort
from fastapi import Depends
from . import service


async def validate_mal_anime(
    mal_id: int, session: AsyncSession = Depends(get_session)
) -> Anime:
    if not (anime := await service.get_anime_by_mal_id(session, mal_id)):
        raise Abort("anime", "not-found")

    return anime


async def validate_anitube_anime(
    anitube_id: int, session: AsyncSession = Depends(get_session)
) -> Anime:
    if not (anime := await service.get_anime_by_anitube(session, anitube_id)):
        raise Abort("anime", "not-found")

    return anime
