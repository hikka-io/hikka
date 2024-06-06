from sqlalchemy.ext.asyncio import AsyncSession
from .utils import build_anime_filters
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Anime, User
from app import meilisearch
from app import constants
from . import service

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from .dependencies import (
    validate_search_anime,
    validate_franchise,
    get_anime_info,
)

from app.schemas import (
    ContentCharacterPaginationResponse,
    AnimePaginationResponse,
    GenreListResponse,
)

from .schemas import (
    AnimeStaffPaginationResponse,
    AnimeEpisodesListResponse,
    AnimeInfoResponse,
    AnimeSearchArgs,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/anime", tags=["Anime"])


@router.post(
    "",
    response_model=AnimePaginationResponse,
    summary="Anime catalog",
)
async def search_anime(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
    search: AnimeSearchArgs = Depends(validate_search_anime),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    if not search.query:
        limit, offset = pagination(page, size)
        total = await service.anime_search_total(session, search)
        anime = await service.anime_search(
            session, search, request_user, limit, offset
        )

        return {
            "pagination": pagination_dict(total, page, limit),
            "list": anime.unique().all(),
        }

    meilisearch_result = await meilisearch.search(
        constants.SEARCH_INDEX_ANIME,
        filter=build_anime_filters(search),
        query=search.query,
        sort=search.sort,
        page=page,
        size=size,
    )

    return await service.anime_meilisearch_watch(
        session, search, request_user, meilisearch_result
    )


# TODO: Move to separate router
@router.get(
    "/genres",
    response_model=GenreListResponse,
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
    response_model=ContentCharacterPaginationResponse,
    summary="Anime characters",
)
async def anime_characters(
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
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
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.anime_staff_count(session, anime)
    staff = await service.anime_staff(session, anime, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": staff.unique().all(),
    }


@router.get(
    "/{slug}/episodes",
    response_model=AnimeEpisodesListResponse,
    summary="Anime episodes",
)
async def anime_episodes(
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime_info),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
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
    response_model=AnimePaginationResponse,
    summary="Anime recommendations",
)
async def anime_recommendations(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
    anime: Anime = Depends(get_anime_info),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.anime_recommendations_count(session, anime)
    recommendations = await service.anime_recommendations(
        session, anime, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": recommendations.unique().all(),
    }


@router.get(
    "/{slug}/franchise",
    response_model=AnimePaginationResponse,
    summary="Franchise entries",
)
async def anime_franchise(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
    anime: Anime = Depends(validate_franchise),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.franchise_count(session, anime)
    franchise = await service.franchise(
        session, anime, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": franchise.unique().all(),
    }
