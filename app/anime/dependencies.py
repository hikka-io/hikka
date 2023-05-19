from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Anime
from app.errors import Abort
from fastapi import Depends
from . import service


# Get anime by slug
async def get_anime_info(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Anime:
    if not (anime := await service.get_anime_info_by_slug(session, slug)):
        raise Abort("anime", "not-found")

    return anime
