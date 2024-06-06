from app.schemas import ContentCharacterPaginationResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User, Manga
from . import service

from .dependencies import (
    validate_search_manga,
    valdidate_manga_info,
    validate_manga,
)

from .schemas import (
    MangaPaginationResponse,
    MangaInfoResponse,
    MangaSearchArgs,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/manga", tags=["Manga"])


@router.post(
    "",
    response_model=MangaPaginationResponse,
    summary="Manga catalog",
)
async def search_manga(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
    search: MangaSearchArgs = Depends(validate_search_manga),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.manga_search_total(session, search)
    anime = await service.manga_search(
        session, search, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.unique().all(),
    }


@router.get(
    "/{slug}",
    response_model=MangaInfoResponse,
    summary="Manga info",
)
async def manga_info(anime: Manga = Depends(valdidate_manga_info)):
    return anime


@router.get(
    "/{slug}/characters",
    response_model=ContentCharacterPaginationResponse,
    summary="Manga characters",
)
async def manga_characters(
    session: AsyncSession = Depends(get_session),
    manga: Manga = Depends(validate_manga),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.manga_characters_count(session, manga)
    characters = await service.manga_characters(session, manga, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": characters.all(),
    }
