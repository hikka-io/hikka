from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_page, get_size
from .schemas import AnimeInfoResponse
from .utils import build_anime_filters
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Anime
from app import meilisearch
from app import constants
from . import service

from .dependencies import (
    validate_search_anime,
    validate_franchise,
    get_anime_info,
)

from .schemas import (
    AnimeCharacterPaginationResponse,
    AnimeSearchPaginationResponse,
    AnimeStaffPaginationResponse,
    AnimeEpisodesListResponse,
    GenreListResposne,
    AnimeSearchArgs,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/anime", tags=["Anime"])


@router.post(
    "",
    response_model=AnimeSearchPaginationResponse,
    summary="Anime catalog",
)
async def search_anime(
    session: AsyncSession = Depends(get_session),
    search: AnimeSearchArgs = Depends(validate_search_anime),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    if not search.query:
        limit, offset = pagination(page, size)
        total = await service.anime_search_total(session, search)
        anime = await service.anime_search(session, search, limit, offset)
        return {
            "pagination": pagination_dict(total, page, limit),
            "list": anime.all(),
        }

    return await meilisearch.search(
        constants.SEARCH_INDEX_ANIME,
        filter=build_anime_filters(search),
        query=search.query,
        sort=search.sort,
        page=page,
        size=size,
    )


@router.get(
    "/genres",
    response_model=GenreListResposne,
    summary="Genres list",
)
async def anime_genres(
    session: AsyncSession = Depends(get_session),
):
    genres = await service.anime_genres(session)
    return {"list": genres.all()}


@router.get(
    "/{slug}",
    response_model=AnimeInfoResponse,
    summary="Anime info",
)
async def anime_slug(anime: Anime = Depends(get_anime_info)):
    return anime


@router.get(
    "/{slug}/characters",
    response_model=AnimeCharacterPaginationResponse,
    summary="Anime characters",
)
async def anime_characters(
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
):
    limit, offset = pagination(page, size)
    total = await service.anime_characters_count(session, anime)
    characters = await service.anime_characters(session, anime, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": characters.all(),
    }


@router.get(
    "/{slug}/staff",
    response_model=AnimeStaffPaginationResponse,
    summary="Anime staff",
)
async def anime_staff(
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
):
    limit, offset = pagination(page, size)
    total = await service.anime_staff_count(session, anime)
    staff = await service.anime_staff(session, anime, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": staff.all(),
    }


@router.get(
    "/{slug}/episodes",
    response_model=AnimeEpisodesListResponse,
    summary="Anime episodes",
)
async def anime_episodes(
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
):
    limit, offset = pagination(page, size)
    total = await service.anime_episodes_count(session, anime)
    episodes = await service.anime_episodes(session, anime, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": episodes.all(),
    }


@router.get(
    "/{slug}/recommendations",
    response_model=AnimeSearchPaginationResponse,
    summary="Anime recommendations",
)
async def anime_recommendations(
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.anime_recommendations_count(session, anime)
    recommendations = await service.anime_recommendations(
        session, anime, limit, offset
    )
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": recommendations.all(),
    }


@router.get(
    "/{slug}/franchise",
    response_model=AnimeSearchPaginationResponse,
    summary="Franchise entries",
)
async def anime_franchise(
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(validate_franchise),
):
    limit, offset = pagination(page, size)
    total = await service.franchise_count(session, anime)
    franchise = await service.franchise(session, anime, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": franchise.all(),
    }
