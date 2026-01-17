from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.service import genres_count
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
            raise Abort("anime", "unknown-producer")

    # Check if provided studios exist
    if len(search.studios) > 0:
        studios = await service.company_count(session, search.studios)
        if studios != len(search.studios):
            raise Abort("anime", "unknown-studio")

    # Check if provided genres exist
    if len(search.genres) > 0:
        genre_names_to_validate = {
            genre[1:] if genre.startswith("-") else genre for genre in search.genres
        }

        valid_genres_count = await genres_count(session, list(genre_names_to_validate))
        
        if valid_genres_count != len(genre_names_to_validate):
            raise Abort("anime", "unknown-genre")

    return search


async def validate_franchise(
    anime: Anime = Depends(get_anime_info),
    session: AsyncSession = Depends(get_session),
):
    if not anime.franchise_id:
        raise Abort("anime", "no-franchise")

    # Dirty fix for empty franchises
    # TODO: fix me (please)
    total = await service.franchise_count(session, anime)
    if total <= 1:
        raise Abort("anime", "no-franchise")

    return anime
