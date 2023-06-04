from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from .schemas import AnimeSearchArgs
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


async def validate_search_anime(
    search: AnimeSearchArgs,
    session: AsyncSession = Depends(get_session),
) -> AnimeSearchArgs:
    # Check if provided producers exist
    if len(search.producers) > 0:
        producers = await service.company_count(session, search.producers)
        if producers != len(search.producers):
            raise Abort("search", "unknown-producer")

    # Check if provided studios exist
    if len(search.studios) > 0:
        studios = await service.company_count(session, search.studios)
        if studios != len(search.studios):
            raise Abort("search", "unknown-studio")

    # Check if provided genres exist
    if len(search.genres) > 0:
        genres = await service.anime_genre_count(session, search.genres)
        if genres != len(search.genres):
            raise Abort("search", "unknown-genre")

    return search
