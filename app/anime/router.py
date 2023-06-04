from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import AnimeInfoResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Anime
from app import constants
from . import meilisearch
from . import service

from .dependencies import (
    validate_search_anime,
    get_anime_info,
)

from .schemas import (
    AnimeSearchPaginationResponse,
    AnimeSearchArgs,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/anime", tags=["Anime"])


@router.post("", response_model=AnimeSearchPaginationResponse)
async def search_anime(
    session: AsyncSession = Depends(get_session),
    search: AnimeSearchArgs = Depends(validate_search_anime),
):
    if not search.query:
        total = await service.anime_search_total(session, search)

        limit, offset = pagination(
            search.page,
            limit=constants.SEARCH_RESULT_LIMIT,
        )

        result = await service.anime_search(session, search, limit, offset)

        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": [anime for anime in result],
        }

    return await meilisearch.anime_search(search)


@router.get("/{slug}", response_model=AnimeInfoResponse)
async def anime_slug(anime: Anime = Depends(get_anime_info)):
    return anime
