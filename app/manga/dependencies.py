from app.common.schemas.manga import MangaSearchArgs
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Manga
from app.errors import Abort
from fastapi import Depends

from app.common.service.read_content import (
    validate_read_content_search_args,
    get_read_content_info_by_slug,
    get_read_content_by_slug,
    manga_models,
)


# Get manga by slug
async def valdidate_manga_info(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Manga:
    if not (
        manga := await get_read_content_info_by_slug(
            session, manga_models, slug
        )
    ):
        raise Abort("manga", "not-found")

    return manga


async def validate_manga(
    slug: str, session: AsyncSession = Depends(get_session)
):
    if not (
        manga := await get_read_content_by_slug(session, manga_models, slug)
    ):
        raise Abort("manga", "not-found")

    return manga


async def validate_search_manga(
    search: MangaSearchArgs,
    session: AsyncSession = Depends(get_session),
) -> MangaSearchArgs:
    await validate_read_content_search_args(session, manga_models, search)
    return search
