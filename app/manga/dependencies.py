from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import MangaSearchArgs
from app.service import magazines_count
from app.service import genres_count
from app.database import get_session
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
    # Check if provided magazines exist
    if len(search.magazines) > 0:
        magazines = await magazines_count(session, search.magazines)
        if magazines != len(search.magazines):
            raise Abort("manga", "unknown-magazine")

    # Check if provided genres exist
    if len(search.genres) > 0:
        genre_names_to_validate = {
            genre[1:] if genre.startswith("-") else genre for genre in search.genres
        }

        valid_genres_count = await genres_count(session, list(genre_names_to_validate))
        
        if valid_genres_count != len(genre_names_to_validate):
            raise Abort("manga", "unknown-genre")

    return search
