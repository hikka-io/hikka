from app.common.schemas.character import ContentCharacterPaginationResponse
from app.common.utils.read_content import build_read_content_filters_ms
from app.utils import paginated_response, sort_by_ids, pagination
from app.common.schemas.novel import NovelSearchArgs
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User, Novel
from app import meilisearch
from app import constants

from app.common.service.read_content import (
    read_content_characters_count,
    read_content_search_total,
    exclude_read_content_ids,
    read_content_characters,
    read_content_search,
    novel_models,
)

from .dependencies import (
    validate_search_novel,
    valdidate_novel_info,
    validate_novel,
)

from .schemas import (
    NovelPaginationResponse,
    NovelInfoResponse,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)


router = APIRouter(prefix="/novel", tags=["Novel"])


@router.post(
    "",
    response_model=NovelPaginationResponse,
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
        exclude_content_ids = await exclude_read_content_ids(
            session, novel_models, search, request_user
        )

        meilisearch_result = await meilisearch.search(
            constants.SEARCH_INDEX_NOVEL,
            filter=build_read_content_filters_ms(search, exclude_content_ids),
            query=search.query,
            sort=search.sort,
            page=page,
            size=size,
        )

        filter_ids = [hit["id"] for hit in meilisearch_result["list"]]

        if not filter_ids:
            return paginated_response([], 0, page, limit)

        total = meilisearch_result["pagination"]["total"]
        offset = 0

    else:
        total = await read_content_search_total(
            session, novel_models, search, filter_ids, request_user
        )

    if total == 0:
        return paginated_response([], 0, page, limit)

    novel = await read_content_search(
        session, novel_models, search, filter_ids, request_user, limit, offset
    )

    novel = novel.unique().all()

    # Database sorts page by catalog sort and we need relevance
    # order Meilisearch returned search results in
    if filter_ids:
        novel = sort_by_ids(novel, filter_ids)

    return paginated_response(novel, total, page, limit)


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
    total = await read_content_characters_count(session, novel_models, novel)

    characters = await read_content_characters(
        session, novel_models, novel, limit, offset
    )

    return paginated_response(characters.all(), total, page, limit)
