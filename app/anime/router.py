from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import AnimeInfoResponse
from .utils import build_anime_filters
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.database import get_session
from app.models import Anime
from app import meilisearch
from app import constants
from . import service

from .dependencies import (
    validate_search_anime,
    get_anime_info,
)

from .schemas import (
    AnimeCharacterPaginationResponse,
    AnimeSearchPaginationResponse,
    AnimeStaffPaginationResponse,
    AnimeEpisodesListResponse,
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
        limit, offset = pagination(search.page, constants.SEARCH_RESULT_LIMIT)
        result = await service.anime_search(session, search, limit, offset)
        return {
            "pagination": pagination_dict(total, search.page, limit),
            "list": [anime for anime in result],
        }

    return await meilisearch.search(
        constants.SEARCH_INDEX_ANIME,
        filter=build_anime_filters(search),
        query=search.query,
        page=search.page,
        sort=search.sort,
    )


@router.get("/{slug}", response_model=AnimeInfoResponse)
async def anime_slug(anime: Anime = Depends(get_anime_info)):
    return anime


@router.get(
    "/{slug}/characters", response_model=AnimeCharacterPaginationResponse
)
async def anime_characters(
    page: int = Depends(get_page),
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
):
    total = await service.anime_characters_count(session, anime)
    limit, offset = pagination(page, constants.SEARCH_RESULT_LIMIT)
    result = await service.anime_characters(session, anime, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [anime_character for anime_character in result],
    }


@router.get("/{slug}/staff", response_model=AnimeStaffPaginationResponse)
async def anime_staff(
    page: int = Depends(get_page),
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
):
    total = await service.anime_staff_count(session, anime)
    limit, offset = pagination(page, constants.SEARCH_RESULT_LIMIT)
    result = await service.anime_staff(session, anime, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [anime_character for anime_character in result],
    }


@router.get("/{slug}/episodes", response_model=AnimeEpisodesListResponse)
async def anime_episodes(
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
):
    episodes = await service.anime_episodes(session, anime)
    return {"list": [episode for episode in episodes]}
