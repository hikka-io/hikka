from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.service import genres_count
from .schemas import MangaSearchArgs
from app.models import Manga
from app.errors import Abort
from fastapi import Depends
from . import service


# Get manga by slug
async def valdidate_manga_info(
    slug: str, session: AsyncSession = Depends(get_session)
) -> Manga:
    if not (manga := await service.get_manga_info_by_slug(session, slug)):
        raise Abort("manga", "not-found")

    return manga


async def validate_manga(
    slug: str, session: AsyncSession = Depends(get_session)
):
    if not (manga := await service.get_manga_by_slug(session, slug)):
        raise Abort("manga", "not-found")

    return manga


async def validate_search_manga(
    search: MangaSearchArgs,
    session: AsyncSession = Depends(get_session),
) -> MangaSearchArgs:
    # # Check if provided producers exist
    # if len(search.producers) > 0:
    #     producers = await service.company_count(session, search.producers)
    #     if producers != len(search.producers):
    #         raise Abort("anime", "unknown-producer")

    # # Check if provided studios exist
    # if len(search.studios) > 0:
    #     studios = await service.company_count(session, search.studios)
    #     if studios != len(search.studios):
    #         raise Abort("anime", "unknown-studio")

    # Check if provided genres exist
    if len(search.genres) > 0:
        genres = await genres_count(session, search.genres)
        if genres != len(search.genres):
            raise Abort("manga", "unknown-genre")

    return search
