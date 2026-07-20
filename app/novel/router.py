from sqlalchemy.ext.asyncio import AsyncSession
from .utils import build_novel_filters_ms
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User, Novel
from app import meilisearch
from app import constants
from . import service

from .dependencies import (
    validate_search_novel,
    valdidate_novel_info,
    validate_novel,
)

from .schemas import (
    NovelCatalogPaginationResponse,
    NovelInfoResponse,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from app.schemas import (
    ContentCharacterPaginationResponse,
    NovelSearchArgs,
)

from app.utils import (
    paginated_response,
    pagination,
)


router = APIRouter(prefix="/novel", tags=["Novel"])


@router.post(
    "",
    response_model=NovelCatalogPaginationResponse,
    summary="Novel catalog",
)
async def search_novel(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_READLIST])
    ),
    search: NovelSearchArgs = Depends(validate_search_novel),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)

    filter_ids = []
    if search.query:
        meilisearch_result = await meilisearch.search(
            constants.SEARCH_INDEX_NOVEL,
            filter=build_novel_filters_ms(search),
            query=search.query,
            sort=search.sort,
            page=page,
            size=size,
        )

        filter_ids = [hit["id"] for hit in meilisearch_result["list"]]

        if not filter_ids:
            return paginated_response([], 0, page, limit)

    total = await service.novel_search_total(session, search, filter_ids)

    if total == 0:
        return paginated_response([], 0, page, limit)

    novel = await service.novel_search(
        session, search, filter_ids, request_user, limit, offset
    )

    return paginated_response(novel.unique().all(), total, page, limit)


@router.get(
    "/{slug}",
    response_model=NovelInfoResponse,
    summary="Novel info",
)
async def novel_info(novel: Novel = Depends(valdidate_novel_info)):
    return novel


@router.get(
    "/{slug}/characters",
    response_model=ContentCharacterPaginationResponse,
    summary="Novel characters",
)
async def novel_characters(
    session: AsyncSession = Depends(get_session),
    novel: Novel = Depends(validate_novel),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.novel_characters_count(session, novel)
    characters = await service.novel_characters(session, novel, limit, offset)

    return paginated_response(characters.all(), total, page, limit)
