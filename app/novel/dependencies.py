from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import NovelSearchArgs
from app.service import magazines_count
from app.service import genres_count
from app.database import get_session
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
        genre_names_to_validate = {
            genre[1:] if genre.startswith("-") else genre for genre in search.genres
        }

        valid_genres_count = await genres_count(session, list(genre_names_to_validate))
        
        if valid_genres_count != len(genre_names_to_validate):
            raise Abort("novel", "unknown-genre")

    return search
