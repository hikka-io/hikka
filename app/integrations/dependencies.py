from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.errors import Abort
from app.integrations.schemas import MALContentTypeEnum
from app.models import Anime
from app.models.content.manga import Manga
from app.models.content.novel import Novel

from . import service


async def validate_mal_content(
    content_type: MALContentTypeEnum,
    mal_id: int,
    session: AsyncSession = Depends(get_session),
) -> Anime | Manga | Novel:
    if not (
        content := await service.get_content_by_mal_id(
            session, content_type, mal_id
        )
    ):
        raise Abort("content", "not-found")

    return content


async def validate_anitube_anime(
    anitube_id: int, session: AsyncSession = Depends(get_session)
) -> Anime:
    if not (anime := await service.get_anime_by_anitube(session, anitube_id)):
        raise Abort("anime", "not-found")

    return anime
