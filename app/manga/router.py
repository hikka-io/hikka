from app.utils import paginated_response, pagination
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import build_manga_filters_ms
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User, Manga
from app import meilisearch
from app import constants
from . import service

from .dependencies import (
    validate_search_manga,
    valdidate_manga_info,
    validate_manga,
)

from .schemas import (
    MangaPaginationResponse,
    MangaInfoResponse,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from app.schemas import (
    ContentCharacterPaginationResponse,
    MangaSearchArgs,
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

    filter_ids = []

    if search.query:
        meilisearch_result = await meilisearch.search(
            constants.SEARCH_INDEX_MANGA,
            filter=build_manga_filters_ms(search),
            query=search.query,
            sort=search.sort,
            page=page,
            size=size,
        )

        filter_ids = [hit["id"] for hit in meilisearch_result["list"]]

        if not filter_ids:
            return paginated_response([], 0, page, limit)

    total = await service.manga_search_total(session, search, filter_ids)

    if total == 0:
        return paginated_response([], 0, page, limit)

    manga = await service.manga_search(
        session, search, filter_ids, request_user, limit, offset
    )

    return paginated_response(manga.unique().all(), total, page, limit)


@router.get(
    "/{slug}",
    response_model=MangaInfoResponse,
    summary="Manga info",
)
async def manga_info(manga: Manga = Depends(valdidate_manga_info)):
    return manga


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

    return paginated_response(characters.all(), total, page, limit)
