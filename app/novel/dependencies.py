from sqlalchemy.ext.asyncio import AsyncSession
from app.service import magazines_count
from app.service import genres_count
from app.database import get_session
from .schemas import NovelSearchArgs
from app.models import Novel
from app.errors import Abort
from fastapi import Depends
from . import service


# Get novel by slug
async def valdidate_novel_info(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Novel:
    if not (novel := await service.get_novel_info_by_slug(session, slug)):
        raise Abort("novel", "not-found")

    return novel


async def validate_novel(
    slug: str, session: AsyncSession = Depends(get_session)
):
    if not (novel := await service.get_novel_by_slug(session, slug)):
        raise Abort("novel", "not-found")

    return novel


async def validate_search_novel(
    search: NovelSearchArgs,
    session: AsyncSession = Depends(get_session),
) -> NovelSearchArgs:
    # Check if provided magazines exist
    if len(search.magazines) > 0:
        magazines = await magazines_count(session, search.magazines)
        if magazines != len(search.magazines):
            raise Abort("novel", "unknown-magazine")

    # Check if provided genres exist
    if len(search.genres) > 0:
        genres = await genres_count(session, search.genres)
        if genres != len(search.genres):
            raise Abort("novel", "unknown-genre")

    return search
